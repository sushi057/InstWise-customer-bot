from typing import Annotated, Callable, List, Literal, TypedDict

from pydantic import BaseModel, Field


class RouterAgentOutput(BaseModel):
    route: Annotated[
        Literal["data_agent", "action_agent"],
        Field(description="The agent to route the user query to."),
    ]


class InternalWorkflowAgents(TypedDict):
    """Internal workflow agents dictionary."""

    query_database: Callable
    action_agent: Callable
    action_agent_tools: List[Callable]
    data_agent: Callable


class InternalWorkflowPrompts(TypedDict):
    """Internal workflow prompts dictionary."""

    schema: str
    nltosql_prompt: str
    abstract_queries_prompt: str
