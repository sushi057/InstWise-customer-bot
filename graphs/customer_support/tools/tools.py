import os
import base64
import requests
from pydantic import BaseModel, Field

from langchain_core.tools import tool
from langchain_core.messages.ai import AIMessage

# from langchain_core.messages import ToolMessage


from graphs.customer_insights.tools.tools import query_database


class FeedbackInput(BaseModel):
    query: str = Field(..., title="The query for the feedback")
    rating: int = Field(..., title="The user's rating")
    feedback: str = Field(..., title="The user's feedback")
    organization_id: str = Field(..., title="The organization id")
    user_email: str = Field(..., title="The user's email")


RAG_API_URL = "https://chat-backend.instwise.app/api/assistant/ask"
headers = {"X-API-KEY": f"{os.getenv('X_API_KEY')}"}

hubspot_api = "https://api.hubapi.com/crm/v3/objects"
hubspot_headers = {
    "Authorization": f'Bearer {os.getenv("HUBSPOT_BEARER_TOKEN")}',
    "Content-Type": "application/json",
}

zendesk_api = "https://instwisehelp.zendesk.com/api/v2"
encoded_credentials = base64.b64encode(
    (f'{os.getenv("ZENDESK_EMAIL")}/token:{os.getenv("ZENDESK_TOKEN")}').encode("utf-8")
).decode("utf-8")
zendesk_headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/json",
}


# Placeholder function for text-to-sql tool, query_database
def call_query_database(query: str):
    return query_database(query)


#


# Used for get_user_info node
def fetch_user_info(user_email: str):
    """
    Fetch user info with the text-to-sql tool.

    Args:
        user_email: The email of the user.
    """
    try:
        response = call_query_database(f"Find the customer with the email {user_email}")
        if response[0].result_set:
            return response[0].result_set[0]
        else:
            return {}
    except Exception as e:
        return {
            "message": "An error occurred while fetching user info",
            "error": str(e),
        }


# fetch_user_info("sarah@hilton.com")


@tool
def solution_rag_call(query: str) -> AIMessage:
    """
    This function sends a query to the RAG API and returns the answer as an AIMessage.

    Parameters:
    - query (str): The query to send to the RAG API.

    Returns:
    - AIMessage: The response from the RAG API as an AIMessage object.
    """
    response = requests.get(
        RAG_API_URL,
        params={"query": query, "company_id": "66158fe71bfe10b58cb23eea"},
        headers=headers,
    )
    return AIMessage(response.json()["results"]["answer"])


@tool
def recommend_features(query: str) -> AIMessage:
    """
    This function sends a query to the RAG API and returns the answer as an AIMessage.

    Parameters:
    - query (str): The query to send to the RAG API.

    Returns:
    - AIMessage: The response from the RAG API as an AIMessage object.
    """

    response = requests.get(
        RAG_API_URL,
        params={
            "query": query,
            "company_id": "66158fe71bfe10b58cb23eea",
            "call_type": "recommendation",
        },
        headers=headers,
    )
    return AIMessage(response.json()["results"]["answer"])


@tool
def upsell_features(query: str) -> AIMessage:
    """
    This function sends a query to the RAG API and returns the answer as an AIMessage.

    Parameters:
    - query (str): The query to send to the RAG API.

    Returns:
    - AIMessage: The response from the RAG API as an AIMessage object.
    """

    response = requests.get(
        RAG_API_URL,
        params={
            "query": query,
            "company_id": "66158fe71bfe10b58cb23eea",
            "call_type": "upsell",
        },
        headers=headers,
    )
    return AIMessage(response.json()["results"]["answer"])


@tool
def collect_feedback(
    query: str,
    rating: int,
    feedback: str,
    organization_id: str,
    user_email: str,
) -> AIMessage:
    """
    Record's user's feedback to the database.

    Args:
        query (str): The query for the feedback.
        rating (int): The user's rating.
        feedback (str): The user's feedback.
        user_email (str): The user's email.
        organization_id (str): The organization id.

    Returns:
        AIMessage: A message confirming the feedback has been collected.
    """
    feedback_data = {
        "query": query,
        "rating": rating,
        "feedback": feedback,
        "organization_id": "66e534d37a7f6e9808c7b921",
        "user_email": user_email,
    }

    # API call to add feedback to the database
    try:
        response = requests.post(
            "https://api-assistant.instwise.app/api/v1/feedback/survey",
            json=feedback_data,
        )
        response.raise_for_status()
        # print(response.json())
        return AIMessage("Your feedback has been recorded.")
    except requests.exceptions.RequestException as e:
        return AIMessage(f"An error occurred while recording your feedback: {e}")
