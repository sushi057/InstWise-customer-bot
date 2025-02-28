from typing import Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str


class AbstractQueryResponse(BaseModel):
    """Response for abstract query"""

    abstract_query: str = Field(..., description="Transformed abstract query")
    final_query: str = Field(..., description="Final query based on user's query")


class QueryResponse(BaseModel):
    table_sources: Optional[str]
    result_set: Optional[List]
    metadata: Dict


class CreateTaskRequest(BaseModel):
    company_name: str = Field(..., description="Company name")
    task_body: str = Field(..., description="Task body")


class CreateTaskResponse(BaseModel):
    id: str = Field(..., description="Task ID")
    company_name: str = Field(..., description="Company name")
    created_at: str = Field(..., description="Task created at")
    body_preview: str = Field(..., description="Task body preview")


class CreateNoteRequest(BaseModel):
    company_name: str = Field(..., description="Company name")
    note_body: str = Field(..., description="Note body")


class CreateNoteResponse(BaseModel):
    id: str = Field(..., description="Note ID")
    company_name: str = Field(..., description="Company name")
    created_at: str = Field(..., description="Note created at")
    body_preview: str = Field(..., description="Note body preview")


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
