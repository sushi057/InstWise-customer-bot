# from langsmith import traceable

from graphs.task_agent.prompts import create_task_agent_prompts
from graphs.task_agent.tools.send_email import send_email
from session.session import TaskSession
from utils.init_model import init_model


def create_task_agent(session: TaskSession):
    """Create task agents for given organization and task name."""

    llm = init_model(fully_specified_name="gpt-4o")

    task_agent_prompts = create_task_agent_prompts(session)

    query_database = session.nltosql_tool

    current_task_data = query_database.invoke(
        task_agent_prompts["current_task_data_prompt"]
    )

    task_agent_runnable = task_agent_prompts["task_agent_main_prompt"].partial(
        task_data=current_task_data
    ) | llm.bind_tools([send_email])

    return task_agent_runnable
