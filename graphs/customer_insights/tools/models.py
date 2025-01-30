from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str


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
