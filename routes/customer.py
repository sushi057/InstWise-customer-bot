from fastapi import APIRouter, HTTPException

from schemas.customer import CheckEmailRequest, CheckEmailResponse
from graphs.customer_insights.tools.tools import query_database

router = APIRouter(tags=["customer"])


@router.post("/get-customer-by-email", response_model=CheckEmailResponse)
async def get_customer_by_email(request: CheckEmailRequest):
    """
    Check if email exists in the database and return details.
    """
    try:
        query = f"Find the customer name associated with the domain {request.email.split('@')[1]} "
        result = query_database(query)

        if result[0].result_set:
            return CheckEmailResponse(
                customer_name=result[0].result_set[0]["name"],
                domain=result[0].result_set[0]["domain"],
            )
        else:
            raise HTTPException(status_code=404, detail="Customer not found.")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
