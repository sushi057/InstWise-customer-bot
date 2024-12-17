from pydantic import BaseModel, EmailStr
from typing import Optional

class CheckEmailRequest(BaseModel):
    org_id: str
    email: EmailStr

class CheckEmailResponse(BaseModel):
    customer_name: Optional[str]
    domain: Optional[str]

