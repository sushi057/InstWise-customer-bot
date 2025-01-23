import os
import json
import requests
from pydantic import BaseModel, EmailStr
from fastapi import HTTPException, status
from dotenv import load_dotenv

from langchain_core.tools import tool

load_dotenv()


class Ticket(BaseModel):
    customer_id: str
    email: EmailStr
    subject: str
    description: str


zendesk_domain = os.getenv("ZENDESK_SUBDOMAIN")
user = f"{os.getenv('ZENDESK_USER', '')}/token"
password = os.getenv("ZENDESK_TOKEN")
headers = {"content-type": "application/json"}


@tool
async def create_zendesk_ticket_for_unresolved_issues(ticket_input: Ticket):
    """
    Create a ticket in Zendesk.

    Args:
    - ticket_input: Ticket data
    """
    if not zendesk_domain or not user or not password or password is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Zendesk credentials are missing. Please check the environment variables.",
        )
    try:
        customer_id = ticket_input.customer_id  # Example customer ID
        requester_email = ticket_input.email
        requester_name = ticket_input.email
        # Prepare the ticket data
        ticket_data = {
            "ticket": {
                "subject": ticket_input.subject
                or "Default Subject",  # Provide a default if subject is missing
                "description": ticket_input.description
                or "Default Description",  # Provide a default if description is missing
                "priority": "normal",  # Ensure a valid priority value
                "requester": {
                    "id": (
                        customer_id if customer_id else None
                    ),  # Dynamically set customer ID or use None
                    "email": (
                        requester_email if requester_email else "unknown@example.com"
                    ),  # Ensure a fallback email
                    "name": (
                        requester_name if requester_name else "Unknown Requester"
                    ),  # Ensure a fallback name
                },
            }
        }
        # Convert the ticket data into JSON
        payload = json.dumps(ticket_data)
        print("zendesk_domain", zendesk_domain)
        zendesk_url = f"https://{zendesk_domain}.zendesk.com/api/v2/tickets"
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
