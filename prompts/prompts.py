import os
import requests
from fastapi import HTTPException
from langchain.prompts import ChatPromptTemplate


#  Fetch prompts for the organization
def fetch_prompts_organization():
    domain = "backend.instwise.app"
    setting_api_key = os.environ["SETTING_API_KEY"]

    # Replace with organization_id
    organization_id = "66158fe71bfe10b58cb23eea"
    url = f"https://{domain}/organizationDetail/{organization_id}/"
    headers = {"accept": "*/*", "x-api-key-local": setting_api_key}

    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except requests.exceptions.HTTPError as e:
        # Better error handling
        raise HTTPException(status_code=response.status_code, detail=str(e))
    except requests.exceptions.RequestException as e:
        # Handle other possible exceptions (e.g., network issues, SSL errors)
        raise HTTPException(status_code=500, detail=str(e))


organization_detail = fetch_prompts_organization()

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", organization_detail["org"]["primary_assistant_prompt"]),
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
            "You are the Solution Agent tasked with resolving customer issues."
            "The primary assistant delegates work to you whenever the user's query has been clarified and requires a solution. Your tasks include:"
            "Using the RAG (Retrieval-Augmented Generation) model to provide accurate and relevant answers to the user’s query."
            "Checking if there are multiple possible solutions from the RAG response and offering clarification options to help the user specify the issue."
            "Asking the user if the solution provided has resolved their problem, if not provide a workaround for the issue."
            "If the problem is not solved, signal the Log Agent to create a ticket with appropriate response to the user."
            "Once the solution is provided, signal the Primary Assistant to continue the conversation with the user."
            "The user is NOT AWARE of the different specialized assistants, so do not mention them; just quietly delegate through function calls. ",
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
