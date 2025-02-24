from typing import Optional

from pydantic import BaseModel, Field


class SupportWorkflowPrompts(BaseModel):
    """Prompts for a specific organization."""

    primary_assistant_prompt: str = Field(description="Primary assistant prompt")
    solution_prompt: str = Field(description="Solution agent prompt")
    followup_prompt: str = Field(description="Followup agent prompt")


class NLTOSQLPrompts(BaseModel):
    """Prompts required for the nltosql tool."""

    schema_prompt: str = Field(
        description="Schema for the organization redshift database"
    )
    abstract_queries_prompt: str = Field(
        description="Abstract queries prompt", alias="abstract_refinement_prompt"
    )
    nltosql_prompt: str = Field(description="NLTOSQL prompt")


class RedshiftConfig(BaseModel):
    """Redshift workspace details."""

    database_name: str = Field(..., description="Database name")
    redshift_work_space: str = Field(
        ..., description="Redshift work space", alias="redshit_work_space"
    )
    redshift_db: str = Field(..., description="Redshift database")


class ModelConfig(BaseModel):
    """Model configuration details."""

    temperature: Optional[float] = Field(
        default=0.5, description="Temperature for the model"
    )
    model: Optional[str] = Field(default="gpt-4o", description="Model name")


class OutreachPrompts(BaseModel):
    """Prompts for customer outreach."""

    outreach_email_generation_prompt: Optional[str] = Field(
        description="Outreach email generation prompt"
    )
    outreach_customer_list_generation_prompt: str = Field(
        description="Outreach customer list generation prompt"
    )


class OrganizationDetail(BaseModel):
    """Organization details from backend API"""

    id: str = Field(description="Organization ID", alias="_id")
    name: str = Field(description="Organization name")

    support_workflow_prompts: SupportWorkflowPrompts

    nltosql_tool_prompts: NLTOSQLPrompts

    internal_solution_prompt: str = Field(description="Internal solution agent prompt")

    email_reply_prompt: Optional[str] = Field(description="Email reply prompt")
    customer_outreach_prompt: Optional[str] = Field(
        description="Customer outreach prompt"
    )

    outreach_prompts: OutreachPrompts

    config_model: ModelConfig

    redshift_config: RedshiftConfig
