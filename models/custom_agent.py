from typing import List, Optional

from pydantic import BaseModel, Field


class AgentTask(BaseModel):
    """Model for individual agent tasks."""

    id: str = Field(..., description="Unique ID of the task", alias="_id")
    agent: str = Field(..., description="ID of the agent this task belongs to")
    name: str = Field(..., description="Name of the task")
    tools: Optional[str] = Field(None, description="Tools used for the task")
    instruction: str = Field(..., description="Instructions for the task")


class AgentConfig(BaseModel):
    """Model for agent configurations."""

    id: str = Field(..., description="Unique ID of the agent", alias="_id")
    name: str = Field(..., description="Name of the agent")
    objective: Optional[str] = Field(None, description="Objective of the agent")
    greeting: Optional[str] = Field(None, description="Greeting message of the agent")
    routing_examples: Optional[str] = Field(
        None, description="Examples for routing to this agent"
    )
    tools_used: Optional[str] = Field(None, description="Tools used by the agent")
    primary_instruction: str = Field(
        ..., description="Primary instructions for the agent"
    )
    organization: str = Field(
        ..., description="ID of the organization this agent belongs to"
    )
    agentInstructions: List[str] = Field(
        [], description="List of agent-specific instructions"
    )
    routing_instruction: Optional[str] = Field(
        None, description="Instructions for routing to this agent"
    )
    tasks: List[AgentTask] = Field(
        [], description="List of tasks associated with this agent"
    )


class AgentConfigList(BaseModel):
    """Model for a list of agent configurations."""

    data: List[AgentConfig]
