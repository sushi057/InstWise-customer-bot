from pydantic import BaseModel
from typing import List, Optional, Dict


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    table_sources: Optional[str]
    result_set: Optional[List]
    metadata: Dict
