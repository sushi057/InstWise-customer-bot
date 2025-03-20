from langchain_core.prompts import ChatPromptTemplate

from session.session import TaskSession


def create_task_agent_prompts(session: TaskSession):
    """Create prompts for task agent details."""

    task_agent_details = session.task_details

    task_agent_main_prompt = ChatPromptTemplate(
        [
            (
                "system",
                f"""
You are a task_agent at {task_agent_details.organization.name}.
Your job is to analyze the given data and generate output based on the given objective.

<agent_context>
To: {task_agent_details.taskAgents.recipient}
Action: {task_agent_details.taskAgents.action}
Task name: {task_agent_details.taskAgents.name}

{task_agent_details.taskAgents.objective}
</agent_context>

<task_data>
{{task_data}}
</task_data>

<task_objective>
{task_agent_details.taskAgents.task_outcome}
</task_objective>

<output_requirements>
1. Analyze the provided task_data according to the task_objective
2. Generate appropriate outputs based on the analysis
3. Take any required actions as specified in the objective
</output_requirements>
""",
            )
        ]
    )

    return task_agent_main_prompt
