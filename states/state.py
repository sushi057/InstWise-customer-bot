from typing import TypedDict, Annotated, Literal, Optional
from langgraph.graph.message import AnyMessage, add_messages
from openai import BaseModel


def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """Push or pop the state"""
    if right is None:
        return left
    if right == "pop":
        return left[:-1]
    return left + [right]


class UserInfo(BaseModel):
    """
    User information

    Args:
        user_id (str): User ID
        user_email (str): User email
        name (str): User name
        pending_issues (str | None): Pending issues
        company (str): Company name
    """

    user_id: str
    user_email: str
    name: str
    pending_issues: str | None
    company: str


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_info: UserInfo
    dialog_state: Annotated[
        list[
            Literal[
                "primary_assistant",
                "investigation_agent",
                "solution_agent",
                "recommendation_agent",
                "upsell_agent",
                "log_agent",
                "survey_agent",
            ]
        ],
        update_dialog_stack,
    ]
