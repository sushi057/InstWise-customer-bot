from pydantic import BaseModel


class CustomerInfo(BaseModel):
    """Customer information"""

    customer_id: str
    customer_email: str
    company_name: str
    start_date: str
