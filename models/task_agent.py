from typing import Optional

from pydantic import BaseModel, Field

from graphs.task_agent.models import TaskName


class AskTaskAgentRequest(BaseModel):
    """Request model for the ask task agent endpoint"""

    query: str = Field(..., description="User query")
    org_id: str = Field(..., description="Organization ID to get details.")
    task_name: TaskName = Field(..., description="Task name to be performed.")
    session_id: Optional[str] = Field(
        None, description="Session ID for the current conversation"
    )


class AskTaskAgentResponse(BaseModel):
    """Response model for the ask task agent endpoint."""

    message: str = Field(..., description="Response message from the task agent")
    session_id: Optional[str] = Field(
        None, description="Session ID for the current conversation"
    )
