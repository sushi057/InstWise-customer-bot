import os
import json
from typing import Callable
import requests
import secrets

from fastapi import HTTPException
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import RunnableLambda

from graphs.customer_support.states.state import State

planhat_mock_api_path = os.path.abspath("data/planhat_mock.json")
# planhat_mock_api_path = "planhat_mock.json"
# os.chdir(os.path.dirname(planhat_mock_api_path))


def load_json():
    with open(planhat_mock_api_path, "r") as f:
        response = json.load(f)
        return response


def create_entry_node(assistant_name: str, new_dialog_state: str) -> Callable:
    def entry_node(state: State) -> dict:
        tool_call_id = state["messages"][-1].tool_calls[0]["id"]
        return {
            "messages": [
                ToolMessage(
                    content=f"The assistant is now the {assistant_name}. Reflect on the above conversation between the primary assistant and the user."
                    f" The user's intent is unsatisfied. Use the provided tools to assist the user. Remember, you are {assistant_name},"
                    " and the investigation, rag and other other action is not complete until after you have successfully invoked the appropriate tool."
                    " If the user changes their mind or needs help for other tasks, call the CompleteOrEscalate function to let the primary primary assistant take control."
                    " Do not mention who you are - just act as the proxy for the assistant.",
                    tool_call_id=tool_call_id,
                )
            ],
            "dialog_state": new_dialog_state,
        }

    return entry_node


# This node will be shared for exiting all specialized assistants
def pop_dialog_state(state: State) -> dict:
    """Pop the dialog stack and return to the main assistant.

    This lets the full graph explicitly track the dialog flow and delegate control
    to specific sub-graphs.
    """
    messages = []
    if state["messages"][-1].tool_calls:
        # Note: Doesn't currently handle the edge case where the llm performs parallel tool calls
        messages.append(
            ToolMessage(
                content="Resuming dialog with the primary assistant. Please reflect on the past conversation and assist the user as needed.",
                tool_call_id=state["messages"][-1].tool_calls[0]["id"],
            )
        )
    return {
        "dialog_state": "pop",
        "messages": messages,
    }


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


#  Fetch prompts for the organization
def fetch_organization_details(org_id: str):
    domain = "backend.instwise.app"
    setting_api_key = os.environ["SETTING_API_KEY"]

    # Replace with organization_id
    url = f"https://{domain}/organizationDetail/{org_id}/"
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


def get_session_id():
    return secrets.token_urlsafe(10)


def visualize_graph(graph):
    with open("./graphs/customer_support/graph.png", "wb") as f:
        f.write(graph.get_graph(xray=True).draw_mermaid_png())
