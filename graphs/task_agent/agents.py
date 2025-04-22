from dotenv import load_dotenv

from graphs.customer_insights.tools.hubspot import (
    create_note_hubspot,
    create_task_hubspot,
)
from graphs.customer_insights.tools.insert_ces_tool import insert_summary_in_redshift
from graphs.task_agent.prompts import create_task_agent_prompts
from graphs.task_agent.tools.email_api.gmail_outreach import send_personalized_emails
from session.session import TaskSession

load_dotenv()


def create_task_agent(session: TaskSession):
    """Create task agents for given organization and task name."""

    llm = session.chat_model

    task_agent_prompts = create_task_agent_prompts(session)

    query_database = session.nltosql_tool

    current_task_data = query_database.invoke(
        session.task_details.taskAgents.data_source
    )

    task_agent_runnable = task_agent_prompts.partial(
        task_data=current_task_data
    ) | llm.bind_tools(
        [
            send_personalized_emails,
            insert_summary_in_redshift,
            create_note_hubspot,
            create_task_hubspot,
        ]
    )

    return task_agent_runnable
