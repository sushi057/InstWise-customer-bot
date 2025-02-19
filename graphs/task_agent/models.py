from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, field_validator

TaskName: TypeAlias = Literal[
    "Negative Sentiment", "Feature Adoption", "Decline in Usage"
]


class Organization(BaseModel):
    """Model for organization details."""

    id: str = Field(..., description="Organization ID.", alias="_id")
    name: str = Field(..., description="Organization name.")

    """Model for task name details."""


class TaskAgentDetails(BaseModel):
    """Task Agent details model"""

    name: TaskName = Field(..., description="Task Agent name.")
    action: str = Field(..., description="Task Agent action.")
    objective: str = Field(..., description="Task Agent objective.")
    recipient: str = Field(..., description="Task Agent recipient.", alias="who")
    data_source: str = Field(..., description="Task Agent trigger.", alias="trigger")
    task_outcome: str = Field(..., description="Task Agent output.", alias="output")
    tools: str = Field(..., description="Task Agent tools.")
    active: bool = Field(..., description="Task Agent active status.")
    frequency: str = Field(..., description="Task Agent frequency.")


class Task(BaseModel):
    """Request model for the task agent details endpoint."""

    org_id: str = Field(..., description="Organization ID to get details.")
    task_name: TaskName = Field(
        description="Name of the task to get details.",
    )


class TaskDetails(BaseModel):
    """Response model for the task agent details endpoint."""

    organization: Organization = Field(..., description="Organization details.")
    taskAgents: TaskAgentDetails = Field(..., description="Task agents details.")

    model_config = ConfigDict(
        json_schema_extra={
            "organization": {"_id": "66158fe71bfe10b58cb23eea", "name": "StaynTouch"},
            "taskAgents": [
                {
                    "name": "Decline in Usage",
                    "action": "Draft Email",
                    "objective": "Outreach to customers when usage declines",
                    "who": "Sent to Customer main contact, from: CS owner, cc: Account Manager, bcc: CRM or CSP tool",
                    "trigger": "Analyze feature or login usage patterns. If a decline is observed, take action.",
                    "output": "Generate email empathizing with the decline, asking for feedback on reasons for reduced usage.",
                    "tools": "CRM, Product Analytics",
                    "active": True,
                    "frequency": "Monthly",
                    "organization": "66158fe71bfe10b58cb23eea",
                }
            ],
        }
    )

    @field_validator("taskAgents", mode="before")
    @classmethod
    def parse_list(cls, v: list) -> dict:
        return v[-1]
