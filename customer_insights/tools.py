import os
import base64
import requests
from dotenv import load_dotenv
from bson.objectid import ObjectId

from pydantic import BaseModel, ValidationError
from langchain_core.tools import tool
from langchain_core.runnables.config import RunnableConfig

load_dotenv()

# HubSpot API
hubspot_api = "https://api.hubapi.com/crm/v3"
hubspot_headers = {
    "Authorization": f'Bearer {os.getenv("HUBSPOT_BEARER_TOKEN")}',
    "Content-Type": "application/json",
}

# Zendesk API
zendesk_api = f'https://{os.getenv("ZENDESK_SUBDOMAIN")}.zendesk.com/api/v2'
encoded_credentials = base64.b64encode(
    (f'{os.getenv("ZENDESK_EMAIL")}/token:{os.getenv("ZENDESK_TOKEN")}').encode("utf-8")
).decode("utf-8")
zendesk_headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/json",
}


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


@tool
def fetch_notes_of_company(company_id: str):
    """
    Fetch HubSpot notes for the given HubSpot ID.

    Args:
        company_id (str): The HubSpot ID of the customer.

    Returns:
        dict: The response message containing the notes.
    """
    try:
        response = requests.get(
            f"{hubspot_api}/objects/companies/{company_id}/associations/notes",
            headers=hubspot_headers,
        ).json()

        notes = []
        for note in response["results"]:
            note_id = note["id"]
            note_response = requests.get(
                f"{hubspot_api}/objects/notes/{note_id}?properties=hs_note_body",
                headers=hubspot_headers,
            ).json()
            notes.append(note_response)
        return notes
    except Exception as e:
        return f"Error fetching HubSpot notes: {e}"


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


@tool
def fetch_organization_by_name(organization_name: str):
    """
    Fetch Zendesk organization for the given organization name.

    Args:
        organization_name (str): The name of the organization.

    Returns:
        str: The response message.
    """
    try:
        response = requests.get(
            f'{zendesk_api}/search.json?query=type:organization name:"{organization_name}"',
            headers=zendesk_headers,
        )
        print(zendesk_api, organization_name)
        return response.json()
    except Exception as e:
        return f"Error fetching Zendesk organization: {e}"


@tool
def fetch_tickets_of_organization(customer_id: str):
    """
    Fetch Zendesk tickets for the given organization.

    Args:
       customer_id (str): The organization ID of the customer.

    Returns:
        str: The response message.
    """
    try:
        # Fetch associated tickets of the organization
        response = requests.get(
            f"{zendesk_api}/organizations/{customer_id}/tickets",
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


@tool
def get_all_customers():
    """
    Get list of all the customers.

    Returns:
        customer_information_list(dict): List of customer information.
    """
    try:
        response = requests.get(
            "https://api-assistant.instwise.app/api/v1/customer/details"
        ).json()
        return response
    except Exception as e:
        return f"Error fetching all customers: {e}"


@tool
def get_customer_information_by_customer_id(customer_id: str, config: RunnableConfig):
    """
    Get customer information by organization id.

    Args:
        customer_id (str): The organization id.
        config (RunnableConfig): The configuration for the graph.

    Returns:
        customer_information(dict): The response message.
    """
    token = config.get("configurable", {}).get("token")
    try:
        response = requests.get(
            f"https://api-assistant.instwise.app/api/v1/customer/details?customer_id={customer_id}&token={token}"
        ).json()
        return response
    except Exception as e:
        return f"Error fetching customer information: {e}"


@tool
def get_login_detail_by_customer_id(customer_id: str, config: RunnableConfig):
    """
    Get login/feature list by organization id.

    Args:
        customer_id (str): The organization id.
        config (RunnableConfig): The configuration for the graph.

    Returns:
        login_detail(dict): The response message.
    """
    token = config.get("configurable", {}).get("token")
    try:
        response = requests.get(
            f"https://api-assistant.instwise.app/api/v1/customer/login-details?customer_id={customer_id}&token={token}"
        ).json()
        return response
    except Exception as e:
        return f"Error fetching login details: {e}"


@tool
def get_feature_list_by_customer_id(customer_id: str, config: RunnableConfig):
    """
    Get feature list by organization id.

    Args:
        customer_id (str): The organization id.
        config (RunnableConfig): The configuration for the graph.

    Returns:
        feature_list(dict): The response message.
    """
    token = config.get("configurable", {}).get("token")
    try:
        response = requests.get(
            f"https://api-assistant.instwise.app/api/v1/customer/features?customer_id={customer_id}&token={token}"
        ).json()
        return response
    except Exception as e:
        return f"Error fetching feature list: {e}"


# Chatdata agent tools
@tool
def get_conversation_by_customer_id(customer_id: str, config: RunnableConfig):
    """
    Get conversation by customer id.

    Args:
        customer_id (ObjectId): The id of the company.
        config (RunnableConfig): The configuration object for the graph.

    Returns:
        conversation_data(dict): The response message.
    """
    token = config.get("configurable", {}).get("token")

    try:
        response = requests.get(
            f"https://api-assistant.instwise.app/api/v1/conversations/customer?customer_id={customer_id}&token={token}"
        ).json()
        return response
    except ValidationError as e:
        return f"Validation Error: {e}"
    except Exception as e:
        return f"Error fetching conversation data: {e}"


@tool
def get_survey_data_by_customer_id(customer_id: str, config: RunnableConfig):
    """
    Get survey data by organization id.

    Args:
        customer_id (str): The organization id.
        config (RunnableConfig): The configuration for the graph

    Returns:
        survey_data(dict): The response message.
    """
    token = config.get("configurable", {}).get("token")
    try:
        response = requests.get(
            f"https://api-assistant.instwise.app/api/v1/feedback/survey?organization_id={customer_id}&token={token}"
        ).json()
        return response
    except Exception as e:
        return f"Error fetching survey data: {e}"


@tool
def get_customer_information_by_name(company_name: str):
    """
    Get the customer_information for the given company name.

    Args:
        company_name (str): The name of the company to search details for.

    Returns:
        customer_information(dict): The response message.
    """
    try:
        response = requests.get(
            f"https://api-assistant.instwise.app/api/v1/customers?customer_name={company_name}"
        ).json()
        zendesk_response = fetch_organization_by_name(company_name)
        response["data"]["help_desk_cust_id"] = zendesk_response["results"][0]["id"]
        return response["data"]
    except Exception as e:
        return f"Error fetching Customer IDs: {e}"


# print(get_customer_information_by_name("hilton"))

query_agent_tools = [get_customer_information_by_name]

tools = [
    fetch_hubspot_contacts,
    fetch_id_of_company,
    fetch_company,
    fetch_contacts_of_company,
    fetch_deals_of_company,
    fetch_notes_of_company,
    fetch_zendesk_tickets,
    fetch_zendesk_organizations,
    fetch_organization_by_name,
    fetch_tickets_of_organization,
    get_all_customers,
    get_customer_information_by_customer_id,
    get_login_detail_by_customer_id,
    get_feature_list_by_customer_id,
    get_conversation_by_customer_id,
    get_survey_data_by_customer_id,
]
