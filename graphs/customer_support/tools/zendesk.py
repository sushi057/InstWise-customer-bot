from graphs.customer_support.tools import tools
from pydantic import BaseModel, EmailStr
import os
import requests
import json
from fastapi import APIRouter, HTTPException, status
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

class Ticket(BaseModel):
    customer_id: str
    email: EmailStr
    subject: str
    description: str


zendesk_domain = os.getenv("ZENDESK_SUBDOMAIN")
user = os.getenv("ZENDESK_USER") + "/token"
password = os.getenv("ZENDESK_TOKEN")
headers = {"content-type": "application/json"}


@tool
async def create_zendesk_ticket(ticket_input: Ticket):
    """
    Create a new ticket in zendesk.
    """
    customer_id = ticket_input.customer_id  # Example customer ID
    requester_email = ticket_input.email
    subject = ticket_input.subject
    description = ticket_input.description
    requester_name = ticket_input.email
    # Prepare the ticket data
    ticket_data = {
        "ticket": {
            "subject": subject
            or "Default Subject",  # Provide a default if subject is missing
            "description": description
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

@tool
async def get_all_tickets():
    """
    Get all tickets from zendesk.
    """
    print("zendesk_domain", zendesk_domain)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {requests.auth._basic_auth_str(user + '/token', password)}",
    }

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