from pydantic import BaseModel, Field


class OrganizationDetail(BaseModel):
    """Organization details from backend API"""

    id: str = Field(description="Organization ID", alias="_id")
    name: str = Field(description="Organization name")
    greeting: str = Field(description="Greeting message")
    primary_prompt: str = Field(description="Primary assistant prompt")
    solution_prompt: str = Field(description="Solution agent prompt")
    followup_prompt: str = Field(description="Followup agent prompt")
    internal_solution_prompt: str = Field(description="Internal solution agent prompt")
    schema_prompt: str = Field(
        description="Schema for the organization redshift database"
    )
    abstract_refinement_prompt: str = Field(description="Abstract queries prompt")
    nltosql_prompt: str = Field(description="NLTOSQL prompt")
    email_reply_prompt: str = Field(description="Email reply prompt")
    customer_outreach_prompt: str = Field(description="Customer outreach prompt")
    outreach_email_generation_prompt: str = Field(
        description="Outreach email generation prompt"
    )
    outreach_customer_list_generation_prompt: str = Field(
        description="Outreach customer list generation prompt"
    )
    temperature: float = Field(description="Temperature for the model")
    model: str = Field(description="Model name")
