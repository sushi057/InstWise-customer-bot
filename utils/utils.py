import os
import requests
from fastapi import HTTPException
from dotenv import load_dotenv

# Load Backend APi
load_dotenv()
instwise_backend_url = os.environ["INSTWISE_BACKEND_URL"]
instwise_secret_key = os.environ["INSTWISE_SECRET_KEY"]
# setting_api_key = os.environ["SETTING_API_KEY"]


def fetch_organization_details(org_id: str):
    """Fetch latest organization details from the backend API."""
    url = f"{instwise_backend_url}/api/v1/organization?organization={org_id}"
    headers = {"accept": "*/*", "x-api-secret-key": instwise_secret_key}

    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except requests.exceptions.HTTPError as e:
        # Better error handling
        raise HTTPException(status_code=response.status_code, detail=str(e))
    except requests.exceptions.RequestException as e:
        # Handle other possible exceptions (e.g., network issues, SSL errors)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print(fetch_organization_details("66158fe71bfe10b58cb23eea"))
