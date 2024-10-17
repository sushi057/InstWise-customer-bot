import os
import base64
import json
import requests
from pydantic import BaseModel, Field

from langchain_core.tools import tool
from langchain_core.messages.ai import AIMessage
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode

from config.config import set_customer_id, get_customer_id


# Base Classes


class FeedbackInput(BaseModel):
    query: str = Field(..., title="The query for the feedback")
    rating: int = Field(..., title="The user's rating")
    feedback: str = Field(..., title="The user's feedback")
    organization_id: str = Field(..., title="The organization id")
    user_email: str = Field(..., title="The user's email")


# Headers

# RAG_API_URL = "https://chat-backend.instwise.app/api/assistant/ask"
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


def fetch_user_info(user_email: str):
    """Looks up the current user info in Hubspot

    Args:
     user_email: the customer to search for

    Returns:
      A response object with customer data

    """
    # response = requests.get(mock_url + "hubspot")

    response = requests.get(
        hubspot_api
        + "/contacts/?properties=firstname, lastname, company, email, pending_issues, customer_id",
        headers=hubspot_headers,
    ).json()

    # configurable = config.get("configurable", {})
    # user_email = configurable.get("user_email")

    try:
        for user in response["results"]:
            if user["properties"]["email"] == user_email:
                # Set customer_id
                if "customer_id" in user["properties"] and get_customer_id() is None:
                    set_customer_id(user["properties"]["customer_id"])
                return user
        return None
    except Exception as e:
        return {
            "message": "An error occurred while fetching user info",
            "error": str(e),
        }


# @tool
def fetch_pending_issues(issue_tickets: list[str]):
    """Fetch if any pending issues for the user from Zendesk

    Returns:
      A response object with user's pending issues
    """
    response = requests.get(zendesk_api + "/tickets", headers=zendesk_headers).json()
    pending_issues = []
    try:
        for ticket in response["tickets"]:
            if str(ticket["id"]) in issue_tickets:
                pending_issues.append(ticket)
        return pending_issues
    except Exception as e:
        return {
            "message": "An error occurred while fetching support status",
            "error": str(e),
        }


@tool()
def lookup_activity(user_id: str):
    """Look up user transactions activity

    Args:
      user_id: Id of customer we're looking for

    Return:
      Returns a response object with customer's transactions history
    """

    # user_id = state["user_info"]["id"]

    planhat_json_path = os.path.abspath("data/planhat_mock.json")
    with open(planhat_json_path, "r") as f:
        response = json.load(f)
    try:
        for item in response:
            if str(item["customerId"]) == user_id:
                return item
        return None
    except Exception as e:
        return {
            "message": "An error occurred while fetching user activity",
            "error": str(e),
        }


@tool
def fetch_support_status(user_id: str):
    """Looks up the current user's support status

    Args:
        user_id: Id of customer we're looking for

    Returns:
      A response object with user's support status
    """


# @tool
# def fetch_support_status(user_id: str):
#     """Looks up the current user's support status

#     Args:
#         user_id: Id of customer we're looking for

#     Returns:
#       A response object with user's support status
#     """
#     # response = requests.get(mock_url + "zendesk")
#     zendesk_json_path = os.path.abspath("data/support_status.json")
#     with open(zendesk_json_path, "r") as f:
#         response = json.load(f)

#     for item in response:
#         if str(item["id"]) == user_id:
#             return item
#     return AIMessage(content="No support status found for this user.")


@tool
def rag_call(query: str) -> AIMessage:
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
def recommendation_rag_call(query: str) -> AIMessage:
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
def suggest_workaround(query: str) -> AIMessage:
    """
    This function searches for a workaround solution to user's current issue..

    Parameters:
    - query (str): The query to send to the RAG API.

    Returns:
    - AIMessage: The response from the RAG API as an AIMessage object.
    """
    workaround_message = (
        "Based on the issue you're facing, I suggest you try the following workaround:."
    )
    return AIMessage(content=workaround_message)


@tool
def log_activity(session_info: dict):
    """
    Captures and log the interaction details from session_info into Planhat.

    Args:
        interaction_details (dict): The details of the interaction to be recorded.

    Returns:
        AIMessage: A confirmation message that the interaction has been recorded.
    """
    # Record the interaction details in both systems.
    planhat_log_data = {
        "session_id": f'{session_info["id"]}',
        "customer_id": f'{session_info["customer_id"]}',
        "details": {
            "subject": f'{session_info["subject"]}',
            "description": f'{session_info["description"]}',
            "status": f'{session_info["status"]}',
            "priority": f'{session_info["priority"]}',
            "created_at": f'{session_info["created_at"]}',
            "assigned_to": f'{session_info["assigned_to"]}',
        },
    }
    with open("data/planhat_log.json", "w") as f:
        json.dump(planhat_log_data, f, indent=4)


@tool
def create_ticket() -> AIMessage:
    """
    Creates a ticket for further investigation with appropriate response to the user.

    Args:
        ticket_details (dict): The details of the ticket to be created.

    Returns:
        AIMessage: A confirmation message that the ticket has been created.
    """
    # Create a ticket in Zendesk.
    confirmation_message = "A ticket has been created for further investigation. You will receive an email confirmation shortly."
    return AIMessage(content=confirmation_message)


@tool
def upsell_rag_call(query: str) -> AIMessage:
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
def personalized_follow_up() -> AIMessage:
    """
    Schedules a personalized follow-up based on the customer's interest.

    Args:
        contact_info (dict): The customer's contact information.
        follow_up_instructions (dict): Instructions for follow-up actions.

    Returns:
        AIMessage: A message confirming the follow-up.
    """
    follow_up_message = "Thank you for your time. I will follow up with you shortly to provide more information on the topic we discussed."
    return AIMessage(content=follow_up_message)


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


def handle_tool_error(state) -> dict:
    """
    Handle tool error and return a dictionary containing error messages.

    Args:
        state: A dictionary representing the state of the tool.

    Returns:
        A dictionary containing error messages.

    """
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list) -> dict:
    """
    Creates a tool node with fallbacks.

    Args:
        tools (list): A list of tools.

    Returns:
        dict: The tool node with fallbacks.
    """
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


def _print_event(event: dict, _printed: set, max_length=1500):
    """
    Print the event information.

    Args:
        event (dict): The event dictionary.
        _printed (set): A set to keep track of printed messages.
        max_length (int, optional): The maximum length of the message to print. Defaults to 1500.
    """
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)
