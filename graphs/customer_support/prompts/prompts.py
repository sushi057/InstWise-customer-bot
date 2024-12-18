from datetime import datetime
from langchain.prompts import ChatPromptTemplate

from . import prompts_local


def create_prompts(org_id: str):
    # organization_detail = fetch_organization_details(org_id)
    organization_detail = prompts_local.organization_details
    primary_assistant_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                organization_detail["org"]["primary_assistant_prompt"],
            ),
            ("placeholder", "{messages}"),
        ]
    ).partial(time=datetime.now())

    solution_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                organization_detail["org"]["solution_prompt"],
            ),
            ("placeholder", "{messages}"),
        ]
    )

    followup_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                organization_detail["org"]["followup_prompt"],
            ),
            ("placeholder", "{messages}"),
        ]
    )

    log_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", organization_detail["org"]["log_prompt"]),
            ("placeholder", "{messages}"),
        ]
    )

    return {
        "primary_assistant_prompt": primary_assistant_prompt,
        "solution_prompt": solution_prompt,
        "followup_prompt": followup_prompt,
        "log_prompt": log_prompt,
    }
