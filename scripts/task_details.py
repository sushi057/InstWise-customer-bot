from graphs.task_agent.helpers import get_task_agent_details
from graphs.task_agent.models import Task

if __name__ == "__main__":
    task = Task(org_id="66158fe71bfe10b58cb23eea", task_name="Sentiment Summarization")
    task_agent_details = get_task_agent_details(task)

    print(task_agent_details)
