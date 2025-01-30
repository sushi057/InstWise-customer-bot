import json
import os

import requests
from dotenv import load_dotenv
from fastapi import HTTPException, status
from langchain_core.tools import tool
from pydantic import BaseModel, EmailStr, Field

from graphs.customer_insights.helpers import fetch_organization_details_by_name

load_dotenv()


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


zendesk_domain = os.getenv("ZENDESK_SUBDOMAIN")
user = f"{os.getenv('ZENDESK_USER', '')}/token"
password = os.getenv("ZENDESK_TOKEN")
headers = {"content-type": "application/json"}
zendesk_url = f"https://{zendesk_domain}.zendesk.com/api/v2/tickets"


@tool()
def create_zendesk_ticket_for_unresolved_issues(
    ticket_input: TicketModel,
):
    """Create a ticket in Zendesk for unresolved customer issues."""
    if not zendesk_domain or not user or not password or password is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Zendesk credentials are missing. Please check the environment variables.",
        )

    try:
        # Fetch organization details for the company name
        organization_details = fetch_organization_details_by_name(
            ticket_input.company_name
        )
        if not organization_details:
            raise Exception("Organization not found")

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

        # Convert the ticket data into JSON
        payload = json.dumps(ticket_data)
        response = requests.post(
            zendesk_url, data=payload, auth=(user, password), headers=headers
        )

        if response.status_code != 201:
            print(
                f"Response Code: {response.status_code}. There was a problem with the request. Exiting."
            )
            print(f"Response Body: {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to create ticket: {response.text}",
            )
        else:
            print("Successfully created the ticket.")
            print(f"Ticket ID: {response.json()['ticket']['id']}")
            return ticket_input
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ticket: {str(e)}",
        )


@tool
async def get_all_tickets():
    """
    Get all tickets from zendesk.
    """
    if not zendesk_domain or not user or not password or password is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Zendesk credentials are missing. Please check the environment variables.",
        )

    zendesk_url = f"https://{zendesk_domain}.zendesk.com/api/v2/tickets"
    response = requests.get(zendesk_url, auth=(user, password))

    if response.status_code == 200:
        data = response.json()
        tickets = data["tickets"]
        return tickets
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to fetch tickets: {response.text}",
        )


# if __name__ == "__main__":
#     print(
#         create_zendesk_ticket_for_unresolved_issues(
#             Ticket(
#                 customer_id="32489327711124",
#                 email="sarah@hilton.com",
#                 subject="Need help with API",
#                 description="Detailed description of the issue",
#             )
#         )
#     )
