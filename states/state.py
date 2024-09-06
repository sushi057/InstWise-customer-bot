from typing import TypedDict, Annotated, Literal, Optional
from langgraph.graph.message import AnyMessage, add_messages

class AgentGraphState(TypedDict):
    messages: Annotated[AnyMessage, add_messages]
    user_info: dict
    thread_id: Optional[str]
    activity: Annotated[dict, add_messages]
    
    