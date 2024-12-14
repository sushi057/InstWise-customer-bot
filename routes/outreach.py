from fastapi import APIRouter, HTTPException
from schemas.outreach import (
    GenerateEmailReplyRequest,
    GenerateEmailReplyResponse,
    SendEmailRequest,
    SendEmailResponse,
)

router = APIRouter()


@router.post("/email-replies", response_model=GenerateEmailReplyResponse)
async def generate_email_reply(request: GenerateEmailReplyRequest):
    """
    Generate an email reply to a customer.
    """
    return GenerateEmailReplyResponse(email_body="Hello, how can I help you?")


@router.post("/send-email", response_model=SendEmailResponse)
async def send_email(request: SendEmailRequest):
    """
    Send an email to a customer.
    """
    return SendEmailResponse(
        email_from="sarah@hilton.com",
        email_to="sushilbhattachan@hotmail.com",
        subject="Hello",
        email_body="Hello, how can I help you?",
    )
