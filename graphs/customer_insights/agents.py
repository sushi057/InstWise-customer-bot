from dotenv import load_dotenv
from pydantic import BaseModel, Field

# from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from graphs.customer_insights.state import AgentStateGraph
from graphs.customer_insights.tools.tools import (
    create_nl2sql_tool,
    # query_database
)

from graphs.customer_insights.prompts import data_agent_prompt_template
from graphs.customer_insights.helpers import create_internal_workflow_prompts

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
llm_mini = ChatOpenAI(model="gpt-4o-mini")


class ValidationResponse(BaseModel):
    response: bool = Field(..., description="The validation response from the agent.")


def create_internal_workflow_agents(org_id: str):
    """Create agents and tools for the internal workflow."""

    # Load prompts
    internal_workflow_prompts = create_internal_workflow_prompts(org_id=org_id)
    query_database = create_nl2sql_tool(
        schema_prompt=internal_workflow_prompts["schema"],
        nltosql_prompt=internal_workflow_prompts["nltosql_prompt"],
        abstract_queries_prompt=internal_workflow_prompts["abstract_queries_prompt"],
    )

    def data_agent(state: AgentStateGraph):
        """This agent will draw insights from the data based on the user query."""

        # Replace with internal_workflow_prompts["data_agent_prompt"]
        data_agent_runnable = data_agent_prompt_template | llm.bind_tools(
            [query_database], parallel_tool_calls=False
        )
        response = data_agent_runnable.invoke(state)
        return {**state, "messages": response}

    return {
        "data_agent": data_agent,
        "query_database": query_database,
    }
