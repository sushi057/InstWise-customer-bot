from langchain_core.prompts import ChatPromptTemplate


def create_workflow_prompts(agent_details: dict):
    primary_assistant_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", agent_details["primary_instruction"]),
            ("placeholder", "{messages}"),
        ]
    )

    workflow_prompts = {}
    for task in agent_details["tasks"]:
        task_name = task["task_name"]
        workflow_prompts[f"{task_name}"] = ChatPromptTemplate.from_messages(
            [
                ("system", task["instruction"]),
                ("placeholder", "{messages}"),
            ]
        )

    return primary_assistant_prompt, workflow_prompts
