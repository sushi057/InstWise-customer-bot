from typing import cast

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI

from graphs.customer_insights.models import InternalWorkflowAgents
from graphs.customer_insights.prompts import (
    action_agent_template,
    data_agent_prompt_template,
)
from graphs.customer_insights.state import AgentStateGraph
from graphs.customer_insights.tools.hubspot import (
    create_note_hubspot,
    create_task_hubspot,
)
from graphs.customer_support.tools.zendesk import (
    create_zendesk_ticket_for_unresolved_issues,
)
from session.session import SessionState
from utils.helpers import call_rag_api

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
llm_mini = ChatOpenAI(model="gpt-4o-mini")

action_agent_tools = [
    create_zendesk_ticket_for_unresolved_issues,
    create_note_hubspot,
    create_task_hubspot,
]


def create_internal_workflow_agents(
    session_state: SessionState,
) -> InternalWorkflowAgents:
    """Create agents and tools for the internal workflow."""

    query_database = session_state.nltosql_tool
    abstract_query_chain = session_state.abstract_query_chain

    def action_agent(state: AgentStateGraph):
        """This agent will execute actions in the CRM, CSM, or Support application."""

        action_agent_runnable = action_agent_template | llm.bind_tools(
            action_agent_tools
        )
        response = action_agent_runnable.invoke({"messages": state["messages"]})
        return {**state, "messages": response}

    def data_agent(state: AgentStateGraph):
        """This agent will draw insights from the data based on the user query."""

        final_query = None
        if isinstance(state["messages"][-1], ToolMessage):
            res = abstract_query_chain.invoke(state["messages"][-2].content)  # type: ignore
            final_query = res.final_query  # type: ignore

        data_agent_runnable = data_agent_prompt_template | llm.bind_tools(
            [query_database], parallel_tool_calls=False
        )
        response = data_agent_runnable.invoke(
            {
                "messages": state["messages"],
                "final_query": final_query,
            }
        )

        return {**state, "messages": response, "final_query": None}

    def product_knowledge_agent(state: AgentStateGraph):
        last_message = cast(str, state["messages"][-1].content)
        response = call_rag_api(query=last_message, org_id=session_state.org_id)

        return {**state, "messages": AIMessage(content=response)}

    return {
        "query_database": query_database,
        "action_agent": action_agent,
        "action_agent_tools": action_agent_tools,
        "data_agent": data_agent,
        "product_knowledge_agent": product_knowledge_agent,
    }
