import os
from datetime import datetime

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate

from graphs.customer_support.models.types import SupportWorkflowPrompts
from utils.helpers import fetch_organization_details

load_dotenv()
DEV_ENV = os.getenv("DEV_ENV", "prod")


def create_prompts(org_id: str) -> SupportWorkflowPrompts:
    organization_detail = fetch_organization_details(org_id)

    primary_assistant_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                organization_detail.primary_prompt,
            ),
            ("placeholder", "{messages}"),
        ]
    ).partial(time=datetime.now())

    solution_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                organization_detail.solution_prompt,
            ),
            ("placeholder", "{messages}"),
        ]
    )

    followup_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", organization_detail.followup_prompt),
            ("placeholder", "{messages}"),
        ]
    )

    return {
        "primary_assistant_prompt": primary_assistant_prompt,
        "solution_prompt": solution_prompt,
        "followup_prompt": followup_prompt,
        "schema_prompt": organization_detail.schema_prompt,
        "nltosql_prompt": organization_detail.nltosql_prompt,
        "abstract_queries_prompt": organization_detail.abstract_refinement_prompt,
    }
