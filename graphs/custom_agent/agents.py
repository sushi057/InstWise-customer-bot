from typing import Annotated, List, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep, RemainingSteps
from langgraph_supervisor import create_supervisor
from langgraph_supervisor.supervisor import create_react_agent
from pydantic import BaseModel, Field

from graphs.custom_agent.prompts import create_workflow_prompts
from graphs.customer_insights.tools.hubspot import (
    create_note_hubspot,
    create_task_hubspot,
)
from graphs.customer_insights.tools.insert_ces_tool import insert_summary_in_redshift
from graphs.task_agent.tools.email_api.gmail_outreach import send_personalized_emails
from session.session import CustomAgentSession
from utils.helpers import call_rag_api


class AgentStateSchema(TypedDict):
    """State schema for the agent"""

    messages: Annotated[list[BaseMessage], add_messages]
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps
    org_id: str


# New response model for the non-interactive supervisor.


class SupervisorResponse(BaseModel):
    """Response model fo the non interactive custom agent supervisor."""

    status: Literal["Success", "Failed"] = Field(
        ..., description="Status of the response; must be 'success' or 'failed'"
    )
    actions: List[str] = Field(
        default_factory=list, description="List of action identifiers"
    )
    notes: str = Field(
        ..., description="Additional notes or details associated with the response"
    )


def create_agents(session_state: CustomAgentSession):
    llm = session_state.chat_model
    agent_details = session_state.agent_details
    primary_assistant_prompt_template, workflow_prompts = create_workflow_prompts(
        agent_details
    )

    query_database = session_state.nltosql_tool
    task_agents = {}

    if agent_details.name == "Renewal Agent":
        all_tools = [send_personalized_emails, query_database]
    else:
        all_tools = [
            insert_summary_in_redshift,
            query_database,
            call_rag_api,
            create_note_hubspot,
            create_task_hubspot,
        ]

    for task in agent_details.tasks:
        task_name = task.name
        task_agents[task_name] = create_react_agent(
            model=llm,
            state_schema=AgentStateSchema,
            tools=all_tools,
            name=task_name,
            prompt=workflow_prompts[task_name],
        )

    supervisor_name = agent_details.name.replace(" ", "_").lower()

    # If session_state indicates non-interactive mode, pass the response model.
    is_interactive = agent_details.non_interactive

    workflow_supervisor = create_supervisor(
        [agent for agent in task_agents.values()],
        state_schema=AgentStateSchema,
        model=llm,
        tools=[],
        prompt=primary_assistant_prompt_template,
        supervisor_name=supervisor_name,
        response_format=SupervisorResponse if not is_interactive else None,
    )

    return workflow_supervisor
