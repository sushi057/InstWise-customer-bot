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
            (
                "system",
                agent_details.primary_instruction
                + "\n\nOrganization id: {org_id}"
                + """
IMPORTANT NOTES:
**Response Handling (Top Priority):** When receiving a response from the child agent, it is crucial to capture and relay the exact full response back to the customer. This includes all details provided by the child agent without omitting any information. Ensure that the response is clear, concise, and accurately reflects the information given by the child agent. This step is vital for maintaining customer trust and ensuring they feel heard and understood.
**Do not call multiple agents. Call only one tool at one time.**
                """,
            ),
            ("placeholder", "{messages}"),
        ]
    )

    workflow_prompts = {}
    if agent_details.tasks:
        for task in agent_details.tasks:
            task_name = task.name
            workflow_prompts[task_name] = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        task.instruction
                        + "\n\nOrganization id: {org_id}"
                        + tool_call_instructions,
                    ),
                    ("placeholder", "{messages}"),
                ]
            )

    return primary_assistant_prompt, workflow_prompts
