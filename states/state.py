from typing import TypedDict, Annotated, Literal, Optional
from langgraph.graph.message import AnyMessage, add_messages


def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """Push or pop the state"""
    if right is None:
        return left
    if right == "pop":
        return left[:-1]
    return left + [right]


class UserInfo(TypedDict):
    user_id: str
    user_name: str
    user_email: str
    company_name: str
    user_mood: Optional[
        Literal["happy", "unhappy", "neutral"]
    ]  # Useful for sentiment analysis


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_info: str
    # user_query: Annotated[list[AnyMessage], add_messages]
    # investigation_response = Annotated[list[AnyMessage], add_messages]
    # solution_response = Annotated[list[AnyMessage], add_messages]
    # pending_issues: Optional[bool]
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
