from datetime import datetime

from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
from langchain_core.messages import ToolMessage

from utils.utils import fetch_organization_details


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


# Visualize graph
def visualize_graph(graph):
    with open("./graphs/customer_insights/graph.png", "wb") as f:
        f.write(graph.get_graph(xray=True).draw_mermaid_png())


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


def create_internal_workflow_prompts(org_id: str):
    """
    Get updated prompts for the internal workflow based on the organization ID.

    Args:
        org_id (str): The organization ID.

    Returns:
        dict: The updated prompts for the internal workflow.
    """
    organization_detail = fetch_organization_details(org_id)

    # data_agent_prompt = ChatPromptTemplate.from_messages(
    #     [
    #         ("system", organization_detail["org"]["data_agent_prompt"]),
    #         ("placeholder", "{messages}"),
    #     ]
    # ).partial(time=datetime.now())

    schema = organization_detail["org"]["schema_prompt"]
    abstract_queries_prompt = organization_detail["org"]["abstract_refinement_prompt"]
    nltosql_prompt = organization_detail["org"]["nltosql_prompt"]

    return {
        # "data_agent_prompt": data_agent_prompt,
        "schema": schema,
        "abstract_queries_prompt": abstract_queries_prompt,
        "nltosql_prompt": nltosql_prompt,
    }
