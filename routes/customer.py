from fastapi import APIRouter, HTTPException

from schemas.customer import CheckEmailRequest, CheckEmailResponse
from graphs.customer_insights.tools.tools import execute_sql_query

router = APIRouter(tags=["customer"])


@router.post("/get-customer-by-email", response_model=CheckEmailResponse)
async def get_customer_by_email(request: CheckEmailRequest):
    """
    Check if email exists in the database and return details.
    """
    try:
        check_customer_query = f"SELECT * FROM reporting.companies WHERE domain = '{request.email.split('@')[1]}'"
        result = execute_sql_query(check_customer_query)

        if result.result_set:
            return CheckEmailResponse(
                customer_name=result.result_set[0]["name"],
                domain=result.result_set[0]["domain"],
            )
        else:
            raise HTTPException(status_code=404, detail="Customer not found.")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
