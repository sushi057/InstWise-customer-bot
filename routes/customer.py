from typing import cast

from fastapi import APIRouter, Depends, HTTPException

from graphs.customer_insights.tools.models import QueryResponse

# from graphs.customer_insights.tools.nltosql_tool import execute_sql_query
from models.customer import CheckEmailRequest, CheckEmailResponse
from session.cache import get_session_state
from session.session import SessionState

router = APIRouter(tags=["customer"])


@router.post("/get-customer-by-email", response_model=CheckEmailResponse)
async def get_customer_by_email(
    request: CheckEmailRequest, session_state: SessionState = Depends(get_session_state)
):
    """
    Check if email exists in the database and return details.
    """
    try:
        check_customer_query = f"SELECT * FROM reporting.companies WHERE domain = '{request.email.split('@')[1]}'"
        execute_sql_query = session_state.execute_sql_query_func
        result = cast(QueryResponse, execute_sql_query(check_customer_query))

        if result.result_set:
            return CheckEmailResponse(
                customer_name=result.result_set[0]["name"],
                domain=result.result_set[0]["domain"],
            )
        else:
            raise HTTPException(status_code=404, detail="Customer not found.")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
