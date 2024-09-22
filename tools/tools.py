import os
from typing import List
import json
import requests
from langchain_core.tools import tool
from langchain_core.messages.ai import AIMessage
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda, RunnableConfig
from langgraph.prebuilt import ToolNode

from states.state import State


# RAG_API_URL = "https://chat-backend.instwise.app/api/assistant/ask"
RAG_API_URL = "http://localhost:8000/api/assistant/ask"
headers = {"X-API-KEY": f"{os.getenv('X_API_KEY')}"}


# @tool
# def fetch_customer_info(customer_name: str = None):
#     """Looks up the current user data in Hubspot

#     Args:
#       customer_name: The customer to search for

#     Returns:
#       A response object with customer data

#     """
#     # response = requests.get(mock_url + "hubspot")
#     hubspot_api = "https://api.hubapi.com/crm/v3/objects"
#     headers = {
#         "Authorization": f'Bearer {os.getenv("HUBSPOT_BEARER_TOKEN")}',
#         "Content-Type": "application/json",
#     }
#     response = requests.get(
#         hubspot_api + "/contacts/?properties=firstname, lastname, company",
#         headers=headers,
#     )
#     return response.json()


@tool
def fetch_user_info(config: RunnableConfig):
    """Fetch current user information from Hubspot mock data

    Args:
      user_email: The customer to search for

    Returns:
      A response object with customer data

    """
    # response = requests.get(mock_url + "hubspot")

    configuration = config.get("configurable", {})
    user_email = configuration.get("user_email")

    try:
        hubspot_json_path = os.path.abspath("data/user_info.json")
        with open(hubspot_json_path, "r") as f:
            response = json.load(f)

        for user in response:
            if user["user_email"] == user_email:
                return user
        return None
    except FileNotFoundError:
        response = {
            "error": "File not found. Please check the file path and try again."
        }


@tool
def fetch_pending_issues(issue_tickets: List[str]):
    """Fetch if any pending issues for the user from Zendesk mock data

    Returns:
      A response object with user's pending issues
    """
    # response = requests.get(mock_url + "zendesk")
    zendesk_json_path = os.path.abspath("data/zendesk_mock.json")
    with open(zendesk_json_path, "r") as f:
        response = json.load(f)

    # pending_issues = []
    # for item in response:
    #     pending_issues.append(item) if item["status"] == "pending" else None

    return None


@tool
def greet_user(user_email: str):
    """Greet the user with their name or company name

    Args:
      state: The customer to search for

    Returns:
      A response object with customer data

    """
    # print(state)
    # user_info = state.get("user_info", {})

    hubspot_json_path = os.path.abspath("data/user_info.json")
    with open(hubspot_json_path, "r") as f:
        response = json.load(f)

    user_info = {}
    for user in response:
        if user["user_email"] == user_email:
            user_info = user

    # greeting_message = f"Hi {user_info['name']}, how can I help you today?"

    return AIMessage(content=str(user_info))


# print(greet_user("jim@test.com"))


@tool
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

    for item in response:
        return item if item["customerId"] == user_id else None


@tool
def fetch_support_status(user_id: str):
    """Looks up the current user's support status

    Args:
        user_id: Id of customer we're looking for

    Returns:
      A response object with user's support status
    """
    # response = requests.get(mock_url + "zendesk")
    zendesk_json_path = os.path.abspath("data/support_status.json")
    with open(zendesk_json_path, "r") as f:
        response = json.load(f)

    for item in response:
        return item if item["id"] == user_id else None

    return "There's a known issue with spa booking."


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
    workaround_message = "Based on the issue you're facing, I suggest you try the following workaround: [Workaround details]."
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


# utility functions


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
