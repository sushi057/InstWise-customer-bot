from pydantic import BaseModel, EmailStr
from datetime import datetime


class Ticket(BaseModel):
    customer_id: str
    email: EmailStr
    subject: str
    description: str
