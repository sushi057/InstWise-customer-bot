from typing import Annotated, Optional

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class Organization(BaseModel):
    oid: str = Field(..., alias="$oid")


class RenewalDate(BaseModel):
    date: datetime = Field(..., alias="$date")


class CreatedAt(BaseModel):
    date: datetime = Field(..., alias="$date")


class UpdatedAt(BaseModel):
    date: datetime = Field(..., alias="$date")


class Customer(BaseModel):
    id: str = Field(..., alias="_id.$oid")
    name: str
    email: EmailStr
    arr: int
    licenses_purchased: int
    licenses_used: int
    renewal_date: RenewalDate
    csm_agent: EmailStr
    account_executive: EmailStr
    health_score: int
    login_count: int
    main_feature_usage_count: int
    total_ticket_count: int
    open_ticket_count: int
    escalated_ticket: int
    closed_ticket_count: int
    organization: Organization
    created_at: CreatedAt = Field(..., alias="createdAt")
    updated_at: UpdatedAt = Field(..., alias="updatedAt")
