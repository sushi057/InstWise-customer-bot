from typing import Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field


class AbstractQueryResponse(BaseModel):
    """Response for abstract query"""

    abstract_query: str = Field(..., description="Transformed abstract query")
    final_query: str = Field(..., description="Final query based on user's query")


class QueryResponse(BaseModel):
    """Response model for SQL query."""

    table_sources: Optional[str]
    result_set: Optional[List]
    metadata: Dict


class CreateTaskRequest(BaseModel):
    """Request model for creating a task."""

    company_name: str = Field(..., description="Company name")
    task_body: str = Field(..., description="Task body")


class CreateNoteRequest(BaseModel):
    """Request model for creating a note."""

    company_name: str = Field(..., description="Company name")
    note_body: str = Field(..., description="Note body")


class CreateNLTOSQLPromptsArgs(TypedDict):
    """Organization specific prompts to create prompt templates for"""

    schema_prompt: str
    abstract_queries_prompt: str
    nltosql_prompt: str
    database_name: str


class CreateNLTOSQLToolArgs(CreateNLTOSQLPromptsArgs):
    """Prompts to create NLTOSQL tool."""

    redshift_work_space: str
    redshift_db: str


class NLTOSQLPrompts(TypedDict):
    """Prompts for NLTOSQL tool."""

    schema_prompt: str
    nltosql_prompt: str
    abstract_queries_prompt: str


class AddCustomerEngagementSummaryArgs(BaseModel):
    """Arguments for add_customer_engagement_summary tool."""

    tenant_id: str = Field(..., description="Tenant ID")
    customer_id: str = Field(..., description="Customer ID")
    week_date: str = Field(..., description="Week date")
    sentiment: str = Field(..., description="Sentiment")
    opportunity: str = Field(..., description="Opportunity")
    risk: str = Field(..., description="Risk")
    followup: str = Field(..., description="Follow-up")
