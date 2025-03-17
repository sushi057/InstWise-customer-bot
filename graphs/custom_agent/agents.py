from langgraph_supervisor import create_supervisor
from langgraph_supervisor.supervisor import create_react_agent

from graphs.custom_agent.prompts import create_workflow_prompts
from session.session import CustomAgentSession
from utils.init_model import init_model


def create_agents(session_state: CustomAgentSession):
    llm = init_model("gpt-4o")
    agent_details = session_state.agent_details
    primary_assistant_prompt_template, workflow_prompts = create_workflow_prompts(
        agent_details
    )

    query_database = session_state.nltosql_tool
    task_agents = {}

    for task in agent_details.tasks:
        task_name = task.name

        task_agents[f"{task_name}"] = create_react_agent(
            model=llm,
            tools=[query_database],
            name=f"{task_name}",
            prompt=workflow_prompts[f"{task_name}"],
        )

    supervisor_name = agent_details.name.replace(" ", "_").lower()
    workflow_supervisor = create_supervisor(
        [agent for agent in task_agents.values()],
        model=llm,
        prompt=primary_assistant_prompt_template + "",
        output_mode="full_history",
        supervisor_name=supervisor_name,
    )

    return workflow_supervisor
