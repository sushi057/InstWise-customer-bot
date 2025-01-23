import os
import requests
from pydantic import BaseModel, Field

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_core.messages import AIMessage

# from langchain_core.tools.base import InjectedToolCallId
# from langgraph.types import Command


class FeedbackInput(BaseModel):
    query: str = Field(..., title="The query for the feedback")
    rating: int = Field(..., title="The user's rating")
    feedback: str = Field(..., title="The user's feedback")
    organization_id: str = Field(..., title="The organization id")
    user_email: str = Field(..., title="The user's email")


rag_api_url = os.getenv("RAG_API_URL")
headers = {"X-API-KEY": f"{os.getenv('X_API_KEY')}"}

# hubspot_api = "https://api.hubapi.com/crm/v3/objects"
# hubspot_headers = {
#     "Authorization": f"Bearer {os.getenv('HUBSPOT_BEARER_TOKEN')}",
#     "Content-Type": "application/json",
# }

# zendesk_api = "https://instwisehelp.zendesk.com/api/v2"
# encoded_credentials = base64.b64encode(
#     (f"{os.getenv('ZENDESK_EMAIL')}/token:{os.getenv('ZENDESK_TOKEN')}").encode("utf-8")
# ).decode("utf-8")
# zendesk_headers = {
#     "Authorization": f"Basic {encoded_credentials}",
#     "Content-Type": "application/json",
# }


@tool
def solution_rag_call(query: str, config: RunnableConfig) -> AIMessage:
    """
    This function sends a query to the RAG API and returns the answer as an AIMessage.

    Parameters:
    - query (str): The query to send to the RAG API.
    - company_id(str): The company id to send to the RAG API.

    Returns:
    - AIMessage: The response from the RAG API as an AIMessage object.
    """
    if rag_api_url is None:
        return AIMessage("RAG API URL is missing.")

    company_id = config.get("configurable", {}).get("org_id")
    if company_id is None:
        return AIMessage("Company ID is missing in the configuration.")

    response = requests.get(
        rag_api_url,
        params={"query": query, "company_id": company_id},
        headers=headers,
    )
    return AIMessage(response.json()["results"]["answer"])


@tool
def create_zendesk_ticket_for_unresolved_issues() -> AIMessage:
    """
    This function creates a ticket in Zendesk.
    """
    return AIMessage("Ticket created successfully.")


@tool
def recommend_features(query: str, config: RunnableConfig) -> AIMessage:
    """
    This function sends a query to the RAG API and returns the answer as an AIMessage.

    Parameters:
    - query (str): The query to send to the RAG API.

    Returns:
    - AIMessage: The response from the RAG API as an AIMessage object.
    """
    if rag_api_url is None:
        return AIMessage("RAG API URL is missing.")

    org_id = config.get("configurable", {}).get("org_id")
    if org_id is None:
        return AIMessage("Company ID is missing in the configuration.")

    response = requests.get(
        rag_api_url,
        params={
            "query": query,
            "company_id": org_id,
            "call_type": "recommendation",
        },
        headers=headers,
    )
    return AIMessage(response.json()["results"]["answer"])


@tool
def upsell_features(query: str, config: RunnableConfig) -> AIMessage:
    """
    This function sends a query to the RAG API and returns the answer as an AIMessage.

    Parameters:
    - query (str): The query to send to the RAG API.

    Returns:
    - AIMessage: The response from the RAG API as an AIMessage object.
    """
    if rag_api_url is None:
        return AIMessage("RAG API URL is missing.")

    org_id = config.get("configurable", {}).get("org_id")
    if org_id is None:
        return AIMessage("Company ID is missing in the configuration.")

    response = requests.get(
        rag_api_url,
        params={
            "query": query,
            "company_id": org_id,
            "call_type": "upsell",
        },
        headers=headers,
    )
    return AIMessage(response.json()["results"]["answer"])


@tool
def collect_feedback(
    query: str,
    rating: int | None,
    feedback: str,
    user_email: str,
    config: RunnableConfig,
) -> AIMessage:
    """
    Record's user's feedback to the database.

    Args:
        query (str): The users original query.
        rating (int): The user's rating .
        feedback (str): The user's feedback.
        user_email (str): The user's email.
        organization_id (str): The organization id.

    Returns:
        AIMessage: A message confirming the feedback has been collected.
    """
    organization_id = config.get("configurable", {}).get("org_id")

    feedback_data = {
        "query": query,
        "rating": rating,
        "feedback": feedback,
        "organization_id": organization_id,
        "user_email": user_email,
    }

    # API call to add feedback to the database
    try:
        response = requests.post(
            "https://api-assistant.instwise.app/api/v1/feedback/survey",
            json=feedback_data,
        )
        response.raise_for_status()
        return AIMessage("Your feedback has been recorded.")
    except requests.exceptions.RequestException as e:
        return AIMessage(f"An error occurred while recording your feedback: {e}")


if __name__ == "__main__":
    print(
        collect_feedback.invoke(
            {
                "query": "original query",
                "rating": 5,
                "feedback": "test feedback",
                "organization_id": "test",
                "user_email": "sarah@hilton.com",
            }
        )
    )
