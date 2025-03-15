from langchain_core.prompts import ChatPromptTemplate

from models.custom_agent import AgentConfig


def create_workflow_prompts(agent_details: AgentConfig):
    tool_call_instructions = """
### Tool Usage:
- When needing to fetch user-specific data (e.g., login details, feature usage), use the `query_database` tool.
- Do not transform user query when calling tool. 
- Send original user query to the tool.
"""

    primary_assistant_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", agent_details.primary_instruction),
            ("placeholder", "{messages}"),
        ]
    )

    workflow_prompts = {}
    if agent_details.tasks:
        for task in agent_details.tasks:
            task_name = task.name
            workflow_prompts[f"{task_name}"] = ChatPromptTemplate.from_messages(
                [
                    ("system", task.instruction + tool_call_instructions),
                    ("placeholder", "{messages}"),
                ]
            )

    return primary_assistant_prompt, workflow_prompts
