import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

from graphs.customer_insights.helpers import fetch_organization_details_by_name
from graphs.customer_insights.tools.models import (CreateNoteRequest,
                                                   CreateNoteResponse,
                                                   CreateTaskRequest,
                                                   CreateTaskResponse)

# Load environment variables
load_dotenv()

hubspot_headers = {
    "Authorization": "Bearer " + os.getenv("HUBSPOT_BEARER_TOKEN", ""),
    "Content-Type": "application/json",
}


@tool
def create_task_hubspot(request: CreateTaskRequest) -> CreateTaskResponse:
    """
    Creates task in hubspot.
    """
    try:
        # Fetch organiztaion details for the company name
        organization_details = fetch_organization_details_by_name(
            customer_name=request.company_name
        )

        if not organization_details:
            raise Exception("Organization not found")

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
                            "associationTypeId": 190,
                        },
                    ],
                },
            ],
        }

        response = requests.post(
            "https://api.hubapi.com/crm/v3/objects/tasks",
            headers=hubspot_headers,
            json=json_data,
        ).json()

        return CreateTaskResponse(
            id=response["id"],
            company_name=request.company_name,
            created_at=response["createdAt"],
            body_preview=response["properties"]["hs_body_preview"],
        )

    except Exception as e:
        raise Exception(f"Error creating task in hubspot: {e}")


@tool
def create_note_hubspot(request: CreateNoteRequest) -> CreateNoteResponse:
    """
    Creates note in hubspot.
    """
    try:
        # Fetch organiztaion details for the company name
        organization_details = fetch_organization_details_by_name(
            customer_name=request.company_name
        )
        if not organization_details:
            raise Exception("Organization not found")

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

        response = requests.post(
            "https://api.hubapi.com/crm/v3/objects/notes",
            headers=hubspot_headers,
            json=json_data,
        ).json()
        print(response)

        return CreateNoteResponse(
            id=response["id"],
            company_name=request.company_name,
            created_at=response["createdAt"],
            body_preview=response["properties"]["hs_body_preview"],
        )
    except Exception as e:
        raise Exception(f"Error creating note in hubspot: {e}")
