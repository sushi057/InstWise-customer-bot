from pydantic import BaseModel, Field


class ZendeskCredentials(BaseModel):
    """Zendesk credentials for API access."""

    subdomain: str = Field(..., description="Zendesk subdomain")
    user: str = Field(..., description="Zendesk user email")
    token: str = Field(..., description="Zendesk API token")
    headers: dict = Field(
        default={"content-type": "application/json"},
        description="Headers for Zendesk API requests",
    )

    @property
    def zendesk_url(self):
        """Construct the Zendesk API URL."""
        return f"https://{self.subdomain}.zendesk.com/api/v2/tickets"

    def __init__(self, **data):
        data["user"] = data["user"] + "/token"
        super().__init__(**data)
