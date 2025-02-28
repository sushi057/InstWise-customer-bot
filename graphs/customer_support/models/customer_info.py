from pydantic import BaseModel


class CustomerInfo(BaseModel):
    """Customer information"""

    customer_id: str | None = None
    customer_email: str | None = None
    company_name: str | None = None
    start_date: str | None = None
