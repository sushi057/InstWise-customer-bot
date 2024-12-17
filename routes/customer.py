from fastapi import APIRouter, HTTPException

from schemas.customer import CheckEmailRequest, CheckEmailResponse
from customer_insights.tools.tools import query_database

router = APIRouter(tags=["customer"])


@router.post("/get-customer-by-email", response_model=CheckEmailResponse)
async def get_customer_by_email(request: CheckEmailRequest):
    """
    Check if email exists in the database and return details.
    """
    try:
        query = f"Check if {request.email} exists in our contacts."
        result = query_database(query)

        if result[0].result_set:
            return CheckEmailResponse(
                customer_name=result[0].result_set[0]["first_name"]
                + " "
                + result[0].result_set[0]["last_name"],
                domain=result[0].result_set[0]["company_name"],
            )
        else:
            return CheckEmailResponse(customer_name="No customer found", domain="")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
