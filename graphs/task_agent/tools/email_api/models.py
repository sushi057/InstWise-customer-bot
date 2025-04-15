from typing import List

from pydantic import BaseModel, Field, field_validator


class OrgData(BaseModel):
    org_id: str
    customer_id: str


# Gmail related models
class GmailTokens(BaseModel):
    refresh_token: str
    token_uri: str
    universe_domain: str
    client_secret: str
    scopes: list[str]
    expiry: str
    client_id: str
    account: str
    token: str


class GmailCredentials(BaseModel):
    client_id: str
    project_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_secret: str
    redirect_uris: list[str]


class EmailCredential(BaseModel):
    """Pydantic model for email credential data."""

    access_token: str = Field(..., description="Access token for email.")
    expires_in: int = Field(
        ..., description="Expiration time of the access token in seconds."
    )
    refresh_token: str = Field(
        ..., description="Refresh token to obtain a new access token."
    )
    scope: list[str] = Field(..., description="Scopes granted for the access token.")
    token_type: str = Field(..., description="Type of the token (e.g., Bearer).")
    id_token: str = Field(..., description="ID token for authentication.")

    @field_validator("scope", mode="before")
    @classmethod
    def split_string_scope(cls, values):
        if isinstance(values, str):
            return values.split(" ")
        return values


class OrgGoogleCredential(BaseModel):
    """Pydantic model for organization's Google credential data."""

    client_id: str = Field(..., description="Client ID of the Google Cloud project.")
    project_id: str = Field(..., description="Project ID of the Google Cloud project.")
    auth_uri: str = Field(..., description="Authorization URI for OAuth 2.0.")
    token_uri: str = Field(
        ...,
        description="Token URI for exchanging authorization codes for access tokens.",
    )
    auth_provider_x509_cert_url: str = Field(
        ..., description="URL for the X.509 certificate of the authorization server."
    )
    client_secret: str = Field(
        ..., description="Client secret of the Google Cloud project."
    )
    redirect_uris: List[str] = Field(..., description="List of allowed redirect URIs.")
    javascript_origins: List[str] = Field(
        ..., description="List of allowed JavaScript origins."
    )


class GoogleUserSession(BaseModel):
    """Pydantic model for user session data."""

    id: str = Field(..., alias="_id", description="Unique identifier for the session.")
    email: str = Field(..., description="User's email address.")
    emailCredential: EmailCredential | None = Field(
        None, description="User's Gmail credentials.", alias="credentials"
    )
    googleId: str = Field(..., description="User's Google ID.")
    isGoogleUser: bool = Field(
        ..., description="Indicates if the user logged in with Google."
    )
    organization: str = Field(
        ..., description="Identifier for the user's organization."
    )
    user: str | None = Field(..., description="Identifier for the user.")
    orgGoogleCredential: OrgGoogleCredential = Field(
        ..., description="Organization's Gmail credentials."
    )


class GoogleUserSessionResponse(BaseModel):
    data: List[GoogleUserSession]


class GmailResponseSchema(BaseModel):
    email_address: str
    user_tokens: GmailTokens
    org_data: OrgData


class GmailOutreachSchema(BaseModel):
    email_address: str
    user_tokens: GmailTokens
    org_data: OrgData
    email_to_recipients: list[str]
    email_cc_recipients: list[str]
    email_subject: str
    email_body: str


# Outlook related models
class OutlookTokens(BaseModel):
    token_type: str
    scope: str
    expires_in: int
    ext_expires_in: int
    access_token: str
    refresh_token: str
    id_token: str
    client_info: str
    id_token_claims: dict
    token_source: str


class OutlookCredentials(BaseModel):
    client_id: str
    client_secret: str
    secret_id: str
    tenant_id: str


class OutlookResponseSchema(BaseModel):
    email_address: str
    user_tokens: OutlookTokens
    org_data: OrgData
    app_credentials: OutlookCredentials


class OutlookOutreachSchema(BaseModel):
    email_address: str
    user_tokens: OutlookTokens
    org_data: OrgData
    app_credentials: OutlookCredentials
    email_to_recipients: list[str]
    email_cc_recipients: list[str]
    email_subject: str
    email_body: str
