import os
import re
import requests
import secrets

from fastapi import HTTPException
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import RunnableLambda


def get_valid_email(input_str: str) -> str:
    """
    Extract and return a valid email from the input string.
    """
    email_regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    match = re.search(email_regex, input_str)
    if match:
        return match.group(0)
    return ""


def handle_tool_error(state) -> dict:
    """
    Handle tool error and return a dictionary containing error messages.
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
