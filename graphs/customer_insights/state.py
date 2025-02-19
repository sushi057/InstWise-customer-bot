from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentStateGraph(TypedDict):
    """
    This represents the overall state of the agent.

    messages: A list of messages that have been exchanged between the user and the agent.
    """

    messages: Annotated[list[AnyMessage], add_messages]
