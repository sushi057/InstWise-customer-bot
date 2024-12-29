from typing import Annotated
from pydantic import BaseModel, EmailStr, Field


class GenerateEmailReplyRequest(BaseModel):
    org_id: str
    user_email: EmailStr
    customer_name: str
    customer_domain: str
    subject: str
    email_body_title: str


class GenerateEmailReplyResponse(BaseModel):
    email_body: str


class GenerateEmailsRequest(BaseModel):
    org_id: str


class GenerateEmailsResponse(BaseModel):
    email_from: EmailStr
    email_to: str
    subject: str
    email_body: str


class PersonalizedEmail(BaseModel):
    email_to: EmailStr
    subject: Annotated[str, "Subject of the email"]
    email_body: Annotated[str, "Well written personalized email body"]


class PersonalizedEmailsList(BaseModel):
    """
    List of personalized emails for customers with negative sentiments.

    Each email has a recipient email, subject, and body.
    """

    emails: list[PersonalizedEmail]


class CustomerWithNegativeSentiments(BaseModel):
    name: str
    email_address: str
    sentiment: Annotated[str, "Customer's overall sentiment"]
    score: int = Field(ge=1, le=5, description="Customers overall sentiment score")
    # feedback: Annotated[str, "Customer's overall feedback well described"]
    # Email: PersonalizedEmails


class CustomerListWithNegativeSentiments(BaseModel):
    """
    List of customers with negative sentiments.

    Each customer has a name, email address, sentiment, and score.
    """

    customers: list[CustomerWithNegativeSentiments]
