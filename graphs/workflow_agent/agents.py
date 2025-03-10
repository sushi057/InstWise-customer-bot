from langgraph_supervisor import create_supervisor
from langgraph_supervisor.supervisor import create_react_agent

from graphs.customer_insights.tools.nltosql_tool import create_nltosql_tool
from graphs.workflow_agent.prompts import create_workflow_prompts
from utils.helpers import fetch_organization_details
from utils.init_model import init_model


def create_agents(agent_details: dict):
    llm = init_model("gpt-4o-mini")
    primary_assistant_prompt_template, workflow_prompts = create_workflow_prompts(
        agent_details
    )

    prompts = fetch_organization_details("66158fe71bfe10b58cb23eea")
    query_database, _ = create_nltosql_tool(
        database_name=prompts.database_name,
        schema_prompt=prompts.schema_prompt,
        nltosql_prompt=prompts.nltosql_prompt,
        abstract_queries_prompt=prompts.abstract_queries_prompt,
        redshift_db=prompts.redshift_db,
        redshift_work_space=prompts.redshift_work_space,
    )

    task_agents = {}

    for task in agent_details["tasks"]:
        task_name = task["name"]

        agent_task_name = task_name.replace(" ", "_")
        task_agents[f"{task_name}"] = create_react_agent(
            model=llm,
            tools=[query_database],
            name=f"{agent_task_name}",
            prompt=workflow_prompts[f"{task_name}"],
        )

    workflow_supervisor = create_supervisor(
        [agent for agent in task_agents.values()],
        model=llm,
        add_handoff_back_messages=False,
        prompt=primary_assistant_prompt_template,
        output_mode="full_history",
    )

    return workflow_supervisor
