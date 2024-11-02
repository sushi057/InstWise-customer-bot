import os
import base64
import requests
from pydantic import BaseModel, Field
from langchain_core.tools import tool


# HubSpot API
hubspot_api = "https://api.hubapi.com/crm/v3"
hubspot_headers = {
    "Authorization": f'Bearer {os.environ["HUBSPOT_BEARER_TOKEN"]}',
    "Content-Type": "application/json",
}

# Zendesk API
zendesk_api = "https://inst9141.zendesk.com/api/v2"
encoded_credentials = base64.b64encode(
    (f'{os.getenv("ZENDESK_EMAIL")}/token:{os.getenv("ZENDESK_TOKEN")}').encode("utf-8")
).decode("utf-8")
zendesk_headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/json",
}


class ToCRMAgent(BaseModel):
    """
    Escalate to this agent to inquire about customer data
    """

    hubspot_id: str = Field(
        ..., description="hubspot id of the customer to fetch CRM Data"
    )


class ToCSMAgent(BaseModel):
    """
    Escalate to this agent to inquire about customer data
    """

    zendesk_id: str = Field(
        ..., description="zendesk id of the customer to fetch CSM Data"
    )


class ToHelpDeskAgent(BaseModel):
    """
    Escalate to this agent to inquire about helpdesk assistance
    """

    pass


class ToChatDataAgent(BaseModel):
    """
    Escalate to this agent to inquire about customer support chat history
    """

    user_id: str = Field(..., description="user id of the customer to fetch Chat Data")


# CRM Agent Tools
@tool()
def fetch_hubspot_contacts():
    """
    Fetch HubSpot contacts for the given HubSpot ID.

    Returns:
        str: The response message.
    """
    # Fetch HubSpot contacts
    try:
        response = requests.get(
            f"{hubspot_api}/objects/contacts",
            headers=hubspot_headers,
        )
        print(response.json())
        return response.json()
    except Exception as e:
        return f"Error fetching HubSpot contacts: {e}"


@tool()
def fetch_id_of_company(company_name: str):
    """
    Fetch id of company for the given company name.

    Args:
        company_name (str): The name of the company.

    Returns:
        int: The company ID.
    """
    try:
        response = requests.post(
            f"{hubspot_api}/objects/companies/search",
            headers=hubspot_headers,
            json={
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "name",
                                "operator": "EQ",
                                "value": company_name,
                            }
                        ]
                    }
                ]
            },
        ).json()
        return response["results"][0]["id"]
    except Exception as e:
        return f"Error fetching HubSpot contacts: {e}"


# print(fetch_id_of_company("Hilton"))


@tool
def fetch_company(company_id: str):
    """
    Fetch HubSpot companies for the given HubSpot ID.

    Args:
        company_id (str): The HubSpot ID of the customer.

    Returns:
        str: The response message.
    """
    try:
        response = requests.get(
            f"{hubspot_api}/objects/companies/{company_id}",
            headers=hubspot_headers,
        )
        return response.json()
    except Exception as e:
        return f"Error fetching HubSpot companies: {e}"


# print(fetch_hubspot_companies("23951489207"))


@tool
def fetch_contacts_of_company(company_id: str):
    """
    Fetch HubSpot contacts for the given company.

    Args:
       company_id (str): The company ID of the customer.

    Returns:
        str: The response message.
    """
    try:
        # Fetch associated contacts of the company
        response = requests.get(
            f"{hubspot_api}/objects/companies/{company_id}/?associations=contacts",
            headers=hubspot_headers,
        ).json()

        associated_contacts = []
        for contact in response["associations"]["contacts"]["results"]:
            contact_id = contact["id"]
            contact_response = requests.get(
                f"{hubspot_api}/objects/contacts/{contact_id}",
                headers=hubspot_headers,
            ).json()
            associated_contacts.append(contact_response)

        return associated_contacts
    except Exception as e:
        return f"Error fetching HubSpot contacts: {e}"


@tool()
def fetch_deals_of_company(company_id: str):
    """
    Fetch HubSpot deals for the given HubSpot ID.

    Args:
        company_id (str): The HubSpot ID of the customer.

    Returns:
        str: The response message.
    """
    try:
        # Fetch assosciated deals of a company
        response = requests.get(
            f"{hubspot_api}/objects/companies/{company_id}/?associations=deals",
            headers=hubspot_headers,
        ).json()

        associated_deals = []
        for deal in response["associations"]["deals"]["results"]:
            deal_id = deal["id"]
            deal_response = requests.get(
                f"{hubspot_api}/objects/deals/{deal_id}",
                headers=hubspot_headers,
            ).json()
            associated_deals.append(deal_response)

        return associated_deals
    except Exception as e:
        return f"Error fetching HubSpot deals: {e}"


# Helpdesk Agent Tools


@tool
def fetch_zendesk_tickets():
    """
    Fetch Zendesk tickets.

    Returns:
        str: The response message.
    """
    try:
        response = requests.get(f"{zendesk_api}/tickets", headers=zendesk_headers)
        return response.json()
    except Exception as e:
        return f"Error fetching Zendesk tickets: {e}"


@tool
def fetch_zendesk_organizations():
    """
    Fetch Zendesk organizations.

    Returns:
        str: The response message.
    """
    try:
        response = requests.get(f"{zendesk_api}/organizations", headers=zendesk_headers)
        return response.json()
    except Exception as e:
        return f"Error fetching Zendesk organizations: {e}"


# print(fetch_zendesk_organizations())


@tool
def fetch_tickets_of_organization(organization_id: str):
    """
    Fetch Zendesk tickets for the given organization.

    Args:
       organization_id (str): The organization ID of the customer.

    Returns:
        str: The response message.
    """
    try:
        # Fetch associated tickets of the organization
        response = requests.get(
            f"{zendesk_api}/organizations/{organization_id}/tickets",
            headers=zendesk_headers,
        )
        response.raise_for_status()
        response = response.json()

        associated_tickets = []
        for ticket in response["tickets"]:
            ticket_id = ticket["id"]
            ticket_response = requests.get(
                f"{zendesk_api}/tickets/{ticket_id}",
                headers=zendesk_headers,
            ).json()
            associated_tickets.append(ticket_response)

        return associated_tickets
    except Exception as e:
        return f"Error fetching Zendesk tickets: {e}"
