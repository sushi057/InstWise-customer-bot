import os
import json
import requests
from langchain_core.tools import tool
from langchain_core.messages.ai import AIMessage
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode


@tool
def fetch_customer_info(customer_name: str = None):
    """Looks up the current user data in Hubspot

    Args:
      customer_name: The customer to search for

    Returns:
      A response object with customer data

    """
    # response = requests.get(mock_url + "hubspot")
    hubspot_api = "https://api.hubapi.com/crm/v3/objects"
    headers = {
        "Authorization": f'Bearer {os.getenv("HUBSPOT_BEARER_TOKEN")}',
        "Content-Type": "application/json",
    }
    response = requests.get(
        hubspot_api + "/contacts/?properties=firstname, lastname, company",
        headers=headers,
    )
    return response.json()


@tool
def lookup_activity(customer_id: str):
    """Look up user transactions activity

    Args:
      customer_id: Id of customer we're looking for

    Return:
      Returns a response object with customer's transactions history
    """
    # response = requests.get(mock_url + "planhat")
    print("Inside lookup_activity")
    planhat_json_path = os.path.abspath("utils/planhat_mock.json")
    with open(planhat_json_path, "r") as f:
        response = json.load(f)
        print(response)
    return response


@tool
def clarify_issue() -> AIMessage:
    """Clarify the issue customer is facing. Check in what issue might it be occuring?

    Return:
      AIMessage: Relevant context in which the issue might be occuring
    """
    response = "I see that youre facing an issue with inventory transactions for the new product."
    return AIMessage(content=response)


@tool
def investigate_issue() -> AIMessage:
    """Investigate wether the issue previously occured either with the current
        cutomer or other customers

    Return:
      AIMessage: Relevant information regarding the issue
    """
    response = "I can see that the issue has had previously occured with you. How were you able to handle it then? Has the previous solution not been working?"
    return AIMessage(content=response)


# @tool
# def provide_solution() -> AIMessage:
#     """Provide stepwise solution for the specific issue faced by the customer

#     Return:
#       AIMessage: Stepwise solution for the user's issue
#     """
#     response = "Here's a stepwise solution for the issue you're facing:"
#     return AIMessage(content=response)


# @tool
def answer_rag(query: str) -> AIMessage:
    """
    This function sends a query to the RAG API and returns the answer as an AIMessage.

    Parameters:
    - query (str): The query to send to the RAG API.

    Returns:
    - AIMessage: The response from the RAG API as an AIMessage object.
    """
    RAG_API_URL = "https://chat-backend.instwise.app/api/assistant/ask"

    headers = {"X-API-KEY": f"{os.getenv('X_API_KEY')}"}

    params = {"query": query, "company_id": "66158fe71bfe10b58cb23eea"}
    response = requests.get(RAG_API_URL, params=params, headers=headers)
    return AIMessage(response.json()["results"]["answer"])


@tool
def offer_additional_support() -> AIMessage:
    """
    Offers additional support and relevant resources to prevent future issues.

    Args:
        guide_available (bool): Whether the relevant guide is available to send.

    Returns:
        AIMessage: A message offering additional resources.
    """
    response = "If this is something that happens occasionally, I can recommend setting up a review step before finalizing transactions. We have a quick guide on that—would you like me to send it to you?"
    return AIMessage(content=response)


@tool
def upsell_recommendation() -> AIMessage:
    """
    Introduces relevant add-ons based on the customer's usage data.

    Args:
        usage_data (dict): Data on the customer's usage of the inventory management system.

    Returns:
        AIMessage: A message suggesting an advanced inventory management module.
    """
    response = "Since you’re handling inventory regularly, have you considered our advanced inventory management module? It includes features like automated transaction reviews and error detection, which could save you time and reduce the risk of mistakes."
    return AIMessage(content=response)


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
    follow_up_message = f"I’ll send over the guide right now and follow up in a few days to see if you need any more help. And if you’re interested, I can arrange a demo for the advanced module."
    return AIMessage(content=follow_up_message)


@tool
def log_activity() -> AIMessage:
    """
    Captures and log the interaction details into Planhat.

    Args:
        interaction_details (dict): The details of the interaction to be recorded.

    Returns:
        AIMessage: A confirmation message that the interaction has been recorded.
    """
    # Record the interaction details in both systems.
    confirmation_message = "The interaction has been recorded successfully in Planhat."
    return AIMessage(content=confirmation_message)


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
