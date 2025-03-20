import json
import os
from logging import getLogger

import requests
from langchain_core.tools import tool

from graphs.task_agent.tools.email_api.models import (
    GmailTokens, GoogleUserSessionResponse)

logger = getLogger(__name__)
logger.setLevel("DEBUG")


def fetch_credentials():
    """Fetch credentials from the backend."""

    try:
        credentials_url = f"{os.getenv('INSTWISE_BACKEND_URL')}/api/v1/organization/google-users?token={os.getenv('ORGANIZATION_TOKEN')}&email=bhattachas@hotmail.com"
        response = requests.get(credentials_url)

        response = GoogleUserSessionResponse.model_validate(response.json())

        user_session = response.data[-1]
        return GmailTokens(
            refresh_token=user_session.emailCredential.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            universe_domain="googleapis.com",
            client_secret=user_session.orgGoogleCredential.client_secret,
            scopes=[
                "https://www.googleapis.com/auth/gmail.modify",
                "https://www.googleapis.com/auth/gmail.compose",
            ],
            expiry="2025-03-21T03:47:17.429615",
            client_id=user_session.orgGoogleCredential.client_id,
            account="",
            token=user_session.emailCredential.access_token,
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching credentials: {e}")
        raise e


# Gmail Outreach
@tool
def send_personalized_emails(emails: str, subject: str, body: str):
    """Send personalized emails to the given list of emails.

    Args:
        emails (list[str]): List of email addresses.
        subject (str): Subject of the email.
        body (str): Body of the email.
    """

    # credentials = fetch_credentials()

    credentials = {
        "account": "",
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "expiry": "2025-03-20T13:46:02.556659",
        "refresh_token": os.getenv("GOOGLE_REFRESH_TOKEN"),
        "scopes": [
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/gmail.compose",
        ],
        "token": os.getenv("GOOGLE_ACCESS_TOKEN"),
        "token_uri": "https://oauth2.googleapis.com/token",
        "universe_domain": "googleapis.com",
    }

    org_data = {
        "org_id": "66158fe71bfe10b58cb23eea",
        "customer_id": "66fc1d0de022f0f3a73f0046",
    }

    host = os.getenv("GMAIL_OUTREACH_API_URL", "")

    # Prepare the payload
    payload = {
        "email_address": "sushilbhattachan@gmail.com",
        "user_tokens": credentials,
        "org_data": org_data,
        "email_to_recipients": [emails],
        "email_cc_recipients": [],
        "email_subject": subject,
        "email_body": body,
    }

    print(f"Sending request to {host}")
    print("Payload structure:")
    print(json.dumps(payload, indent=2))

    # Make the POST request
    try:
        response = requests.post(
            host,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=120,
        )

        # Check if the request was successful
        response.raise_for_status()

        # Print the response
        print("Response:")
        try:
            print(json.dumps(response.json(), indent=2))
        except json.JSONDecodeError:
            print(f"Raw response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")


if __name__ == "__main__":
    # print(fetch_credentials())
    print(
        send_personalized_emails.invoke(
            {"emails": "suvash2077@gmail.com", "subject": "Test", "body": "Test"}
        )
    )
