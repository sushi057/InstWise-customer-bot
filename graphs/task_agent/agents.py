# from langsmith import traceable

from config.init_model import init_model
from graphs.customer_insights.tools.tools import create_nl2sql_tool
from graphs.task_agent.models import Task
from graphs.task_agent.prompts import create_task_agent_prompts
from graphs.task_agent.tools.send_email import send_email
from utils.helpers import fetch_organization_details


def create_task_agent(task: Task):
    """Create task agents for given organization and task name."""

    llm = init_model(fully_specified_name="gpt-4o")

    task_agent_prompts = create_task_agent_prompts(task)

    prompts = fetch_organization_details(task.org_id)
    query_database, _ = create_nl2sql_tool(
        schema_prompt=prompts.schema_prompt,
        nltosql_prompt=prompts.nltosql_prompt,
        abstract_queries_prompt=prompts.abstract_refinement_prompt,
    )

    current_task_data = query_database.invoke(
        task_agent_prompts["current_task_data_prompt"]
    )

    # @traceable(name="task_agent", run_type="chain")
    task_agent_runnable = task_agent_prompts["task_agent_main_prompt"].partial(
        task_data=current_task_data
    ) | llm.bind_tools([send_email])

    return task_agent_runnable
