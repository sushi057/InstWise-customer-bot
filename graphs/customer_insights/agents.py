from typing import Annotated, Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from graphs.customer_insights.state import AgentStateGraph
from graphs.customer_insights.tools.tools import (
    create_nl2sql_tool,
    # query_database
)

from graphs.customer_insights.prompts import (
    data_agent_prompt_template,
    router_prompt_template,
    action_agent_template,
)
from graphs.customer_insights.helpers import create_internal_workflow_prompts
from graphs.customer_support.tools.zendesk import (
    create_zendesk_ticket_for_unresolved_issues,
)

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
llm_mini = ChatOpenAI(model="gpt-4o-mini")


class RouterAgentOutput(BaseModel):
    route: Annotated[
        Literal["data_agent", "action_agent"],
        Field(description="The agent to route the user query to."),
    ]


action_agent_tools = [create_zendesk_ticket_for_unresolved_issues]


def create_internal_workflow_agents(org_id: str):
    """Create agents and tools for the internal workflow."""

    # Load prompts
    internal_workflow_prompts = create_internal_workflow_prompts(org_id=org_id)
    query_database = create_nl2sql_tool(
        schema_prompt=internal_workflow_prompts["schema"],
        nltosql_prompt=internal_workflow_prompts["nltosql_prompt"],
        abstract_queries_prompt=internal_workflow_prompts["abstract_queries_prompt"],
    )

    def action_agent(state: AgentStateGraph):
        """This agent will execute actions in the CRM, CSM, or Support application."""

        # Replace with internal_workflow_prompts["action_agent_prompt"]
        action_agent_runnable = action_agent_template | llm.bind_tools(
            action_agent_tools
        )
        response = action_agent_runnable.invoke({"messages": state["messages"]})
        return {**state, "messages": response}

    def data_agent(state: AgentStateGraph):
        """This agent will draw insights from the data based on the user query."""

        # Replace with internal_workflow_prompts["data_agent_prompt"]
        data_agent_runnable = data_agent_prompt_template | llm.bind_tools(
            [query_database], parallel_tool_calls=False
        )
        response = data_agent_runnable.invoke({"messages": state["messages"]})
        return {**state, "messages": response}

    return {
        "query_database": query_database,
        "action_agent": action_agent,
        "action_agent_tools": action_agent_tools,
        "data_agent": data_agent,
    }
