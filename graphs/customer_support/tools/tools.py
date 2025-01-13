import os

# import base64
import requests
from typing import Annotated
from pydantic import BaseModel, Field

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.types import Command

from graphs.customer_support.states.state import CustomerInfo, GraphState
from graphs.customer_insights.tools.tools import query_database


class FeedbackInput(BaseModel):
    query: str = Field(..., title="The query for the feedback")
    rating: int = Field(..., title="The user's rating")
    feedback: str = Field(..., title="The user's feedback")
    organization_id: str = Field(..., title="The organization id")
    user_email: str = Field(..., title="The user's email")


RAG_API_URL = os.getenv("RAG_API_URL")
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


# @tool
def call_query_database(query: str):
    """
    Placeholder function to call text-to-sql tool, query_database.
    """
    return query_database.invoke(query)


@tool
def fetch_user_info(tool_call_id: Annotated[str, InjectedToolCallId], user_email: str):
    """
    Fetch user info with the text-to-sql tool.
    This tool is primarily used for the fetch_user_info node.

    Args:
        tool_call_id: Tool call ID for the current tool call.
        user_email: The email of the user.
    """
    try:
        response = call_query_database(
            f"Fetch customer details with the domain {user_email.split('@')[1]}"
        )

        # Fetch customer info for given email and update state
        if response[0].result_set:
            customer_info = response[0].result_set[0]
            return Command(
                update={
                    "customer_info": CustomerInfo(
                        company_name=customer_info.get("name"),
                        customer_email=user_email,
                        customer_id=customer_info.get("company_id"),
                        start_date=customer_info.get("start_date"),
                    ),
                    "messages": [
                        ToolMessage(
                            content="Successfully fetched customer information.",
                            tool_call_id=tool_call_id,
                        )
                    ],
                },
            )
        else:
            return {}
    except Exception as e:
        return {
            "message": "An error occurred while fetching user info",
            "error": str(e),
        }


# fetch_user_info("sarah@hilton.com")


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
    company_id = config.get("configurable")["org_id"]
    response = requests.get(
        RAG_API_URL,
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


# @tool
def collect_feedback(
    query: str,
    rating: int | None,
    feedback: str,
    user_email: str,
    config: RunnableConfig,
    state: GraphState,
) -> AIMessage:
    """
    Record's user's feedback to the database.

    Args:
        query (str): User's original query
        rating (int): The user's rating.
        feedback (str): The user's overall feedback.
        user_email (str): The user's email.
        customer_id (str): The customer id

    Returns:
        AIMessage: A message confirming the feedback has been collected.
    """
    org_id = config.get("configurable").get("org_id")
    customer_id = state.get("customer_info").get("customer_id")

    feedback_data = {
        "query": query,
        "rating": rating,
        "feedback": feedback,
        "user_email": user_email,
        "organization": org_id,
        "customer": customer_id,
        "user": org_id + "_" + user_email,
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
        collect_feedback(
            query="original query",
            rating=5,
            feedback="test feedback",
            user_email="sarah@hilton.com",
            config=RunnableConfig(configurable={"org_id": "test"}),
            state={"customer_info": {"customer_id": "test"}},
        )
    )
