from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import AnyMessage, add_messages
from pydantic import BaseModel


def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """Push or pop the state"""
    if right is None:
        return left
    if right == "pop":
        return left[:-1]
    return left + [right]


class CustomerInfo(BaseModel):
    customer_id: str
    customer_email: str
    company_name: str
    start_date: str


class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    customer_info: CustomerInfo
    pending_issues: list[str]
    internal_user: bool
