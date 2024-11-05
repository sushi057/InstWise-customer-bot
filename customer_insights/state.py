from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentStateGraph(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    crm_agent_response: str
    csm_agent_response: str
    helpdesk_agent_response: str
    chatdata_agent_response: str
