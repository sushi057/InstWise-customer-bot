from pydantic import BaseModel, EmailStr


class GenerateEmailReplyRequest(BaseModel):
    org_id: str
    user_email: EmailStr
    customer_name: str
    customer_domain: str
    subject: str
    email_body_title: str


class GenerateEmailReplyResponse(BaseModel):
    email_body: str


class SendEmailRequest(BaseModel):
    org_id: str


class SendEmailResponse(BaseModel):
    email_from: EmailStr
    email_to: str
    subject: str
    email_body: str
