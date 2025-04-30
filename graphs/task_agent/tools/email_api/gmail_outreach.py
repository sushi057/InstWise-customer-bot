import json
import os
from logging import getLogger

import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

from graphs.task_agent.tools.email_api.models import (
    GmailTokens,
    GoogleUserSessionResponse,
)

logger = getLogger(__name__)
logger.setLevel("DEBUG")

load_dotenv()


def fetch_credentials():
    """Fetch credentials from the backend."""

    try:
        base_url = os.getenv("INSTWISE_BACKEND_URL")
        organization_token = os.getenv("ORGANIZATION_TOKEN")

        credentials_url = f"{base_url}/api/v1/organization/google-users?token={organization_token}&email=bhattachas@hotmail.com"
        response = requests.get(credentials_url)

        response = GoogleUserSessionResponse.model_validate(response.json())

        user_session = response.data[1]

        if not user_session.emailCredential:
            raise Exception("User session does not have email credentials")

        return GmailTokens(
            account="",
            client_id=user_session.orgGoogleCredential.client_id,
            client_secret=user_session.orgGoogleCredential.client_secret,
            refresh_token=user_session.emailCredential.refresh_token,
            scopes=[
                "https://www.googleapis.com/auth/gmail.modify",
                "https://www.googleapis.com/auth/gmail.compose",
                "https://www.googleapis.com/auth/gmail.write",
            ],
            expiry="2525-04-03T03:47:17.429615",
            token=user_session.emailCredential.access_token,
            token_uri="https://oauth2.googleapis.com/token",
            universe_domain="googleapis.com",
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

    credentials = fetch_credentials()

    org_data = {
        "org_id": "66158fe71bfe10b58cb23eea",
        "customer_id": "66fc1d0de022f0f3a73f0046",
    }

    host = os.getenv("GMAIL_OUTREACH_API_URL", "")

    # Prepare the payload
    payload = {
        "email_address": "sushilbhattachan@gmail.com",
        "user_tokens": credentials.model_dump(),
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
    send_personalized_emails.invoke(
        {"emails": "suvash2077@gmail.com", "subject": "Test", "body": "Test"}
    )
