from datetime import datetime
from logging import getLogger

import requests
from langchain_core.messages import AIMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_core.tools import tool

from graphs.customer_insights.helpers import fetch_organization_details_by_name
from graphs.customer_insights.tools.models import CreateNoteRequest, CreateTaskRequest

logger = getLogger(__name__)


@tool
def create_task_hubspot(request: CreateTaskRequest, config: RunnableConfig):
    """Creates task in hubspot."""
    try:
        session_state = config.get("configurable", {})["session_state"]

        # Fetch organization details for the company name
        organization_details = fetch_organization_details_by_name(
            customer_name=request.company_name,
            session_state=session_state,
        )

        if not organization_details:
            return AIMessage(f"Organization not found for {request.company_name}")

        # Create task data
        json_data = {
            "properties": {
                "hs_timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "hs_task_body": request.task_body,
            },
            "associations": [
                {
                    "to": {
                        "id": organization_details.hubspot_company_id,
                    },
                    "types": [
                        {
                            "associationCategory": "HUBSPOT_DEFINED",
                            "associationTypeId": 192,
                        },
                    ],
                },
            ],
        }

        hubspot_headers = session_state.hubspot_headers

        response = requests.post(
            "https://api.hubapi.com/crm/v3/objects/tasks",
            headers=hubspot_headers,
            json=json_data,
        )
        if not response.ok:
            logger.warning(f"Hubspot task creation failed: {response.status_code}")
            return AIMessage(
                f"HubSpot API error: {response.status_code} - {response.text}"
            )
        response = response.json()

        return AIMessage(
            f"Successfully created the task in HubSpot with ID: {response['id']}"
        )
    except Exception as e:
        logger.error(f"Error creating task in HubSpot: {e}")
        return AIMessage(f"Error creating task in HubSpot: {e}")


@tool
def create_note_hubspot(request: CreateNoteRequest, config: RunnableConfig):
    """Creates note in hubspot."""
    try:
        session_state = config.get("configurable", {})["session_state"]
        # Fetch organization details for the company name
        organization_details = fetch_organization_details_by_name(
            customer_name=request.company_name,
            session_state=session_state,
        )

        if not organization_details:
            return AIMessage(f"Organization not found for {request.company_name}")

        # Create note data
        json_data = {
            "properties": {
                "hs_timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "hs_note_body": request.note_body,
            },
            "associations": [
                {
                    "to": {
                        "id": organization_details.hubspot_company_id,
                    },
                    "types": [
                        {
                            "associationCategory": "HUBSPOT_DEFINED",
                            "associationTypeId": 190,
                        },
                    ],
                },
            ],
        }

        hubspot_headers = session_state.hubspot_headers

        response = requests.post(
            "https://api.hubapi.com/crm/v3/objects/notes",
            headers=hubspot_headers,
            json=json_data,
        )
        if not response.ok:
            logger.warning(f"HubSpot note creation failed: {response.status_code}")
            return AIMessage(
                f"HubSpot API error: {response.status_code} - {response.text}"
            )
        response = response.json()

        logger.info(
            f"Successfully created the note in HubSpot with ID: {(response['id'],)}",
        )

        return AIMessage(
            f"Successfully created the note in HubSpot with ID: {response['id']}"
        )
    except Exception as e:
        logger.error(f"Error creating note in HubSpot: {e}")
        return AIMessage(f"Error creating note in HubSpot: {e}")
        return AIMessage(f"Error creating note in HubSpot: {e}")
