import os
from dotenv import load_dotenv
from datetime import datetime
from langchain.prompts import ChatPromptTemplate

from graphs.customer_support.prompts.prompts_local import organization_details
from utils.helpers import fetch_organization_details

load_dotenv()
DEV_ENV = os.getenv("DEV_ENV", "prod")


def create_prompts(org_id: str):
    if DEV_ENV == "prod":
        organization_detail = fetch_organization_details(org_id)
    else:
        organization_detail = organization_details

    primary_assistant_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                organization_detail["org"]["primary_prompt"],
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

    return {
        "primary_assistant_prompt": primary_assistant_prompt,
        "solution_prompt": solution_prompt,
        "followup_prompt": followup_prompt,
        "schema_prompt": organization_detail["org"]["schema_prompt"],
        "nltosql_prompt": organization_detail["org"]["nltosql_prompt"],
        "abstract_queries_prompt": organization_detail["org"][
            "abstract_refinement_prompt"
        ],
    }
