from typing import Optional

from pydantic import BaseModel, Field


class OrganizationDetail(BaseModel):
    """Organization details from backend API"""

    id: str = Field(description="Organization ID", alias="_id")
    name: str = Field(description="Organization name")

    primary_prompt: str = Field(description="Primary assistant prompt")
    solution_prompt: str = Field(description="Solution agent prompt")
    followup_prompt: str = Field(description="Followup agent prompt")

    schema_prompt: str = Field(
        description="Schema for the organization redshift database"
    )
    abstract_queries_prompt: str = Field(
        description="Abstract queries prompt", alias="abstract_refinement_prompt"
    )
    nltosql_prompt: str = Field(description="NLTOSQL prompt")

    internal_solution_prompt: str = Field(description="Internal solution agent prompt")

    email_reply_prompt: Optional[str] = Field(description="Email reply prompt")
    customer_outreach_prompt: Optional[str] = Field(
        description="Customer outreach prompt"
    )

    outreach_email_generation_prompt: Optional[str] = Field(
        description="Outreach email generation prompt"
    )
    outreach_customer_list_generation_prompt: str = Field(
        description="Outreach customer list generation prompt"
    )

    temperature: Optional[float] = Field(
        default=0.5, description="Temperature for the model"
    )
    model: Optional[str] = Field(default="gpt-4o", description="Model name")

    database_name: str = Field(..., description="Database name")
    redshift_work_space: str = Field(
        ..., description="Redshift work space", alias="redshit_work_space"
    )
    redshift_db: str = Field(..., description="Redshift database")
