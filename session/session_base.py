from graphs.customer_insights.tools.nltosql_tool import (
    create_execute_sql_query_function,
    create_nltosql_tool,
)
from models.organization import OrganizationDetail
from utils.helpers import fetch_organization_details


class SessionState:
    """Base class for Session State."""

    def __init__(self, org_id: str, session_id: str):
        self.org_id = org_id
        self.session_id = session_id
        self.org_details: OrganizationDetail = fetch_organization_details(org_id)

        self.customer_info = None

        if self.org_details:
            """Create execute_sql_query_func and nlto_sql_tool based on the organization details."""

            workgroup_name = self.org_details.redshift_work_space
            database_name = self.org_details.database_name

            self.execute_sql_query_func = create_execute_sql_query_function(
                workgroup_name, database_name
            )

            self.nltosql_tool, self.abstract_query_chain = create_nltosql_tool(
                database_name=database_name,
                redshift_work_space=workgroup_name,
                redshift_db=self.org_details.redshift_db,
                schema_prompt=self.org_details.schema_prompt,
                nltosql_prompt=self.org_details.nltosql_prompt,
                abstract_queries_prompt=self.org_details.abstract_queries_prompt,
            )

            print("Created execute_sql_query_func and nlto_sql_tool")

    def set_customer_info(self, *, customer_id: str, customer_email: str):
        self.customer_info = {"id": customer_id, "email": customer_email}
