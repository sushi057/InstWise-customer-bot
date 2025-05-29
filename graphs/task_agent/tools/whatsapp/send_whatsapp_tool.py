import json
import os
from langchain_core.tools import tool
import requests
from dotenv import load_dotenv

load_dotenv()

@tool
def send_whatsapp_message(message: str, organization_id: str):
    """Send a whatsapp message to the business organization.

    Args:
        message (str): The message to send.
        organization_id (str): Organization ID of the business organization.
    """
    url = f"{os.getenv('NODE_SERVER_URL')}/send-whatsapp"
    print(f"Sending message to {organization_id}")
    node_server_url = os.getenv("NODE_SERVER_URL")
    print(f"Node Server URL: {node_server_url}")
    try:
        response = requests.post(url, json={"message": message, "organization_id": organization_id})
        print(f"Response: {response.json()}")

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    send_whatsapp_message.invoke(
       {"message":"Hello, from python server!", "organization_id":"66158fe71bfe10b58cb23eea"}
    )

