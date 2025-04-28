import json
from logging import getLogger

import requests
from langchain_core.messages import AIMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_core.tools import tool
from pydantic import BaseModel, EmailStr, Field

from graphs.customer_insights.helpers import fetch_organization_details_by_name

logger = getLogger(__name__)


class TicketModel(BaseModel):
    company_name: str = Field(..., description="Company name")
    email: EmailStr = Field(..., description="Requester's email")
    subject: str = Field(..., description="Ticket subject")
    description: str = Field(..., min_length=1, description="Ticket description")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "123",
                "company_name": "Example Company",
                "email": "customer@example.com",
                "subject": "Need help with API",
                "description": "Detailed description of the issue",
            }
        }


@tool()
def create_zendesk_ticket_for_unresolved_issues(
    ticket_input: TicketModel, config: RunnableConfig
):
    """Create a ticket in Zendesk for unresolved customer issues."""
    try:
        session_state = config.get("configurable", {})["session_state"]  # type: ignore

        # Fetch organization details for the company name
        organization_details = fetch_organization_details_by_name(
            ticket_input.company_name,
            session_state,
        )

        if not organization_details:
            return AIMessage(f"Organization not found for {ticket_input.company_name}")

        # Prepare the ticket data
        ticket_data = {
            "ticket": {
                "subject": ticket_input.subject
                or "Default Subject",  # Provide a default if subject is missing
                "description": ticket_input.description
                or "Default Description",  # Provide a default if description is missing
                "priority": "normal",  # Ensure a valid priority value
                "requester": {
                    "id": organization_details.zendesk_org_id,
                    "email": ticket_input.email,
                    "name": ticket_input.email,
                },
            }
        }

        zendesk_credentials = session_state.zendesk_credentials

        zendesk_url = zendesk_credentials.zendesk_url
        user = zendesk_credentials.user
        password = zendesk_credentials.token
        headers = zendesk_credentials.headers

        # Convert the ticket data into JSON
        payload = json.dumps(ticket_data)
        response = requests.post(
            zendesk_url,
            data=payload,
            auth=(user, password),
            headers=headers,
            timeout=10,
        )

        # Minimal error handling and concise logging
        if not response.ok:
            logger.warning(
                f"Zendesk ticket creation failed: {response.status_code} - {response.text}"
            )
            return AIMessage(
                f"Zendesk API error: {response.status_code} - {response.text}"
            )
        else:
            ticket_id = response.json()["ticket"]["id"]

            logger.info(f"Zendesk ticket created: {ticket_id}")
            return AIMessage(
                f"Zendesk ticket created successfully with ID: {ticket_id}"
            )
    except Exception as e:
        logger.error(f"Zendesk ticket creation unexpected error: {e}")
        return AIMessage(f"An error occured while creating the ticket: {str(e)}")
