from dotenv import load_dotenv
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI

from graphs.customer_insights.prompts import data_agent_prompt_template
from graphs.customer_insights.state import AgentStateGraph
from graphs.customer_insights.tools.hubspot import (
    create_note_hubspot,
    create_task_hubspot,
)
from graphs.customer_support.tools.zendesk import (
    create_zendesk_ticket_for_unresolved_issues,
)
from session.session import SessionState

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)


def create_internal_workflow_agents(
    session_state: SessionState,
):
    """Create agents and tools for the internal workflow."""

    query_database = session_state.nltosql_tool
    abstract_query_chain = session_state.abstract_query_chain

    data_agent_tools = [
        query_database,
        create_zendesk_ticket_for_unresolved_issues,
        create_note_hubspot,
        create_task_hubspot,
    ]

    def data_agent(state: AgentStateGraph):
        """This agent will draw insights from the data based on the user query."""

        final_query = ""
        if isinstance(state["messages"][-1], ToolMessage):
            res = abstract_query_chain.invoke(state["messages"][-2].content)  # type: ignore
            final_query = res.final_query  # type: ignore

        data_agent_runnable = data_agent_prompt_template | llm.bind_tools(
            data_agent_tools
        )
        response = data_agent_runnable.invoke(
            {
                "messages": state["messages"],
                "final_query": final_query,
            }
        )

        return {**state, "messages": response, "final_query": None}

    return data_agent, data_agent_tools
