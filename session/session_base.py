import logging

from graphs.customer_insights.tools.nltosql_tool import (
    create_execute_sql_query_function,
    create_nltosql_tool,
)
from graphs.customer_support.models.customer_info import CustomerInfo
from utils.helpers import fetch_organization_details

logger = logging.getLogger(__name__)


class SessionState:
    """Base class for Session State."""

    def __init__(self, org_id: str, session_id: str):
        self.org_id = org_id
        self.session_id = session_id
        self.customer_info: CustomerInfo = CustomerInfo()
        logger.info(
            f"Initializing SessionState for org_id: {org_id}, session_id: {session_id}"
        )

        try:
            self.org_details = fetch_organization_details(org_id)

            if not self.org_details:
                logger.error(f"Session: {session_id} Organization details not found.")
                raise ValueError(
                    f"Organization details not found for session_id: {session_id}"
                )
            else:
                workgroup_name = self.org_details.redshift_work_space
                redshift_db = self.org_details.redshift_db

                self.execute_sql_query_func = create_execute_sql_query_function(
                    workgroup_name, redshift_db
                )

                self.nltosql_tool, self.abstract_query_chain = create_nltosql_tool(
                    database_name=self.org_details.database_name,
                    redshift_work_space=workgroup_name,
                    redshift_db=self.org_details.redshift_db,
                    schema_prompt=self.org_details.schema_prompt,
                    nltosql_prompt=self.org_details.nltosql_prompt,
                    abstract_queries_prompt=self.org_details.abstract_queries_prompt,
                )

                logger.info(
                    f"Session {session_id}: Successfully created tools for org_id: {org_id}"
                )
        except Exception as e:
            logger.error(f"Error fetching organization details: {e}")
            raise

    def set_customer_info(
        self,
        *,
        customer_id: str,
        customer_email: str,
        company_name: str,
        start_date: str | None,
    ):
        self.customer_info = CustomerInfo(
            customer_id=customer_id,
            customer_email=customer_email,
            company_name=company_name,
            start_date=start_date,
        )
        logger.info(
            f"Setting customer info for session_id: {self.session_id}, customer_id: {customer_id}"
        )
