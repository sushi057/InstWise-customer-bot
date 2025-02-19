from typing import Annotated, Literal, Optional, TypedDict

from langgraph.graph.message import AnyMessage, add_messages

from graphs.customer_support.models.customer_info import CustomerInfo


def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """Push or pop the state"""
    if right is None:
        return left
    if right == "pop":
        return left[:-1]
    return left + [right]


class GraphState(TypedDict):
    """State of the graph"""

    messages: Annotated[list[AnyMessage], add_messages]
    customer_info: CustomerInfo
    pending_issues: list[str]
    internal_user: bool
    dialog_state: Literal["followup_agent", "solution_agent"]
