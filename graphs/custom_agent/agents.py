from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep, RemainingSteps
from langgraph_supervisor import create_supervisor
from langgraph_supervisor.supervisor import create_react_agent

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

    workflow_supervisor = create_supervisor(
        [agent for agent in task_agents.values()],
        state_schema=AgentStateSchema,
        model=llm,
        tools=[],
        prompt=primary_assistant_prompt_template,
        supervisor_name=supervisor_name,
    )

    return workflow_supervisor
