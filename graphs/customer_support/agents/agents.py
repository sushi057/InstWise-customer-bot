from typing import Literal, cast
from langgraph.types import Command, interrupt
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from config.config import set_customer_info
from graphs.customer_insights.tools.tools import create_nl2sql_tool
from graphs.customer_support.states.state import CustomerInfo

from config.openai_model import get_openai_model
from graphs.customer_support.states.state import GraphState
from graphs.customer_support.prompts.prompts import create_prompts
from graphs.customer_support.tools.agent_routes import (
    CompleteOrEscalate,
    ToFollowUpAgent,
    ToSolutionAgent,
)
from graphs.customer_support.tools.tools import (
    solution_rag_call,
    recommend_features,
    upsell_features,
    collect_feedback,
)
from graphs.customer_support.tools.zendesk import (
    create_zendesk_ticket_for_unresolved_issues,
)

from graphs.customer_support.helpers.helpers import get_valid_email


def create_agents(org_id: str):
    """Create agents for the customer support graph"""
    llm = get_openai_model(model="gpt-4o")
    prompts = create_prompts(org_id)

    # Create NL2SQL tool
    call_query_database = create_nl2sql_tool(
        schema_prompt=prompts["schema_prompt"],
        nltosql_prompt=prompts["nltosql_prompt"],
        abstract_queries_prompt=prompts["abstract_queries_prompt"],
    )

    # Define tools for the agents
    primary_assistant_tools = [call_query_database, ToSolutionAgent, ToFollowUpAgent]
    solution_tools = [
        solution_rag_call,
        create_zendesk_ticket_for_unresolved_issues,
        CompleteOrEscalate,
    ]
    followup_tools = [
        recommend_features,
        upsell_features,
        call_query_database,
        collect_feedback,
        CompleteOrEscalate,
    ]

    # Entry node for the graph
    def fetch_user_info(
        state: GraphState, config: RunnableConfig
    ) -> Command[Literal["primary_assistant", "__end__"]]:
        """
        Get user info from database based on the user type.
        If the user is an internal user, get the customer info with the email from the config else ask for the email address.
        """

        configurable = config.get("configurable", {})
        internal_user = configurable["internal_user"]

        # Get customer_email based on the chat_type
        ## If the user is not a internal user, ask for email address
        if not internal_user:
            last_human_message = cast(str, state["messages"][-1].content)

            # Ask for email during initial conversation, if email is provided make sure its a valid email
            ## Message asking user email initially
            if "@" not in last_human_message:
                return Command(
                    update={
                        "messages": AIMessage(
                            content="Hi, Could you please provide your email address so that I can assist you better?"
                        )
                    },
                    goto="__end__",
                )
            else:
                customer_email = get_valid_email(last_human_message)
                if not customer_email:
                    return Command(
                        update={
                            "messages": AIMessage(
                                "Please provide a valid email address so that I can assist you better."
                            )
                        },
                        goto="__end__",
                    )
        else:
            customer_email = configurable["customer_email"]

        # Fetch customer info with the customer_email from the database
        try:
            response = call_query_database.invoke(
                f"Fetch customer details with the domain {customer_email.split('@')[1]}"
            )

            # Fetch customer info for given email and update customer_info in state
            if response[0].result_set:
                customer_info = response[0].result_set[0]

                # Update global customer object
                set_customer_info(
                    {
                        "customer_id": customer_info.get("company_id"),
                        "customer_email": customer_email,
                        # "company_name": customer_info.get("name"),
                    }
                )

                # Update customer info and internal user type in graph state
                return Command(
                    goto="primary_assistant",
                    update={
                        "customer_info": CustomerInfo(
                            company_name=customer_info.get("name"),
                            customer_email=customer_email,
                            customer_id=customer_info.get("company_id"),
                            start_date=customer_info.get("start_date"),
                        ),
                        "internal_user": internal_user,
                    },
                )
            else:
                return Command(
                    goto="__end__",
                    update={
                        "messages": AIMessage(
                            content="Sorry, I couldn't find any information for the provided email address. Please try again with a different email address."
                        )
                    },
                )
        except Exception as e:
            raise e
            # return {
            #     "message": "An error occurred while fetching user info",
            #     "error": str(e),
            # }

    def primary_assistant(
        state: GraphState,
    ) -> Command[
        Literal[
            "solution_agent", "followup_agent", "primary_assistant_tools", "__end__"
        ]
    ]:
        """
        Primary Assistant
        """
        primary_assistant_runnable = prompts[
            "primary_assistant_prompt"
        ] | llm.bind_tools(primary_assistant_tools)

        response = primary_assistant_runnable.invoke(state)

        # Add tool message for routing to the Solution Agent or Follow-up Agent
        if response.tool_calls:
            if response.tool_calls[0]["name"] == "ToSolutionAgent":
                tool_call_id = response.tool_calls[-1]["id"]
                tool_message = {
                    "role": "tool",
                    "content": "Transferring the user to the Solution Agent.",
                    "tool_call_id": tool_call_id,
                }

                return Command(
                    goto="solution_agent",
                    update={
                        "messages": [response, tool_message],
                        "dialog_state": "solution_agent",
                    },
                )

            elif response.tool_calls[0]["name"] == "ToFollowUpAgent":
                tool_call_id = response.tool_calls[-1]["id"]
                tool_message = {
                    "role": "tool",
                    "content": "Transferring the user to the Follow-up Agent.",
                    "tool_call_id": tool_call_id,
                }

                return Command(
                    goto="followup_agent",
                    update={
                        "messages": [response, tool_message],
                        "dialog_state": "followup_agent",
                    },
                )
            else:
                return Command(
                    goto="primary_assistant_tools",
                    update={"messages": response},
                )

        return Command(update={"messages": response})

    def solution_agent(
        state: GraphState,
    ) -> Command[Literal["solution_agent_tools", "__end__"]]:
        """
        Solution Agent
        """
        solution_runnable = prompts["solution_prompt"] | llm.bind_tools(solution_tools)

        response = solution_runnable.invoke(state)

        if response.tool_calls:
            if response.tool_calls[0]["name"] == CompleteOrEscalate.name:
                tool_message = {
                    "role": "tool",
                    "content": "Transferring the user to the Primary Assistant.",
                    "tool_call_id": response.tool_calls[-1]["id"],
                }
                return Command(
                    goto="primary_assistant",
                    update={"messages": [response, tool_message], "dialog_state": None},
                )
            else:
                return Command(
                    goto="solution_agent_tools", update={"messages": response}
                )
        return Command(update={"messages": response})

        # return {**state, "messages": response}

    def followup_agent(
        state: GraphState,
    ) -> Command[Literal["followup_agent_tools", "__end__"]]:
        """
        Followup Agent
        """
        followup_runnable = prompts["followup_prompt"] | llm.bind_tools(followup_tools)

        response = followup_runnable.invoke(state)
        if response.tool_calls:
            if response.tool_calls[0]["name"] == CompleteOrEscalate.name:
                tool_message = {
                    "role": "tool",
                    "content": "Transferring the user to the Primary Assistant.",
                    "tool_call_id": response.tool_calls[-1]["id"],
                }
                return Command(
                    goto="primary_assistant",
                    update={"messages": [response, tool_message], "dialog_state": None},
                )
            else:
                return Command(
                    goto="followup_agent_tools", update={"messages": response}
                )
        return Command(update={"messages": response})
        # return {**state, "messages": response}

    def human_node(state: GraphState) -> Command[Literal["followup_agent"]]:
        """
        Human node that takes user input and routes to the followup agent.
        """
        user_input = interrupt(value="")
        return Command(
            goto="followup_agent", update={"role": "human", "content": user_input}
        )

    return {
        "fetch_user_info": fetch_user_info,
        "primary_assistant": primary_assistant,
        "primary_assistant_tools": primary_assistant_tools,
        "solution_agent": solution_agent,
        "solution_agent_tools": solution_tools,
        "followup_agent": followup_agent,
        "followup_agent_tools": followup_tools,
        "human_node": human_node,
    }
