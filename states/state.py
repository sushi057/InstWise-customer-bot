from typing import TypedDict, Annotated, Literal, Optional
from langgraph.graph.message import AnyMessage, add_messages


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
    user_info: UserInfo
    user_query: Annotated[list[AnyMessage], add_messages]
    investigation_response = Annotated[list[AnyMessage], add_messages]
    solution_response = Annotated[list[AnyMessage], add_messages]
    pending_issues: Optional[bool]
