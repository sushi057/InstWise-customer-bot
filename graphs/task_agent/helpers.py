import os

import requests
from dotenv import load_dotenv

from graphs.task_agent.models import Task, TaskDetails

load_dotenv()


def get_task_agent_details(
    task: Task,
) -> TaskDetails:
    """Get task agent details for given organization and task name from backend."""

    try:
        if not os.getenv("SETTING_API_KEY"):
            raise Exception("SETTING_API_KEY is not set in environment variables.")

        headers = {
            "x-api-key-local": os.getenv("SETTING_API_KEY"),
        }
        # Fetch task agent details
        response = requests.get(
            f"https://api-assistant.instwise.app/api/v1/organization/66158fe71bfe10b58cb23eea/task_agent/public?name={task.task_name}",
            headers=headers,
        )
        response.raise_for_status()

        data = response.json()
        if not data["taskAgents"]:
            raise Exception(
                f"Task agent details not found for task_name: '{task.task_name}'",
            )

        task_details_response = TaskDetails.model_validate(data)
        return task_details_response

    except Exception as e:
        raise e


if __name__ == "__main__":
    task = Task(org_id="66158fe71bfe10b58cb23eea", task_name="Decline in Usage")
    task_agent_details = get_task_agent_details(task)
    print(task_agent_details)
