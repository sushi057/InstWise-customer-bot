import os
import requests
from fastapi import HTTPException
from langchain.prompts import ChatPromptTemplate

from customer_support.utils.utils import fetch_organization_details
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
    )

    greeting_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are the Greetings Agent,first node in the customer support workflow, responsible for welcoming customers to the support system. Your tasks include:"
                "Immediately fetching the user information with the given user_email from Hubspot and greeting the user by their name or company name."
                "Checking if the user has any pending issues based on their open tickets."
                "Listening to user's queries or inquiries and responding to them in a friendly and professional manner."
                "If pending issues are found, ask the user if they are inquiring about those issues."
                "Your objective is to make the user feel welcome and streamline the support process by addressing any ongoing cases early."
                "Once the initial greeting is complete, signal the Primary Assistant continue the conversation with the user."
                "The user is NOT AWARE of the different specialized assistants, so do not mention them; just quietly delegate through function calls. ",
            )
        ]
    )

    investigation_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", organization_detail["org"]["investigation_prompt"]),
            ("placeholder", "{messages}"),
        ]
    )

    solution_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                organization_detail["org"]["solution_prompt"],
            ),
            ("placeholder", "{messages}"),
        ]
    )

    recommendation_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", organization_detail["org"]["recommendation_prompt"]),
            ("placeholder", "{messages}"),
        ]
    )

    upsell_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", organization_detail["org"]["upsell_prompt"]),
            ("placeholder", "{messages}"),
        ]
    )

    survey_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", organization_detail["org"]["survey_prompt"]),
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
        "greeting_prompt": greeting_prompt,
        "investigation_prompt": investigation_prompt,
        "solution_prompt": solution_prompt,
        "recommendation_prompt": recommendation_prompt,
        "upsell_prompt": upsell_prompt,
        "survey_prompt": survey_prompt,
        "log_prompt": log_prompt,
    }
