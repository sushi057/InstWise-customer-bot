from typing import Callable, Optional

from graphs.customer_insights.graph import create_insights_graph
from graphs.customer_insights.tools.nltosql_tool import (
    create_execute_sql_query_function,
    create_nltosql_tool,
)
from graphs.customer_support.graph.graph import create_support_graph
from models.organization import OrganizationDetail
from utils.helpers import fetch_organization_details


class SessionState:
    def __init__(self, org_id: str, session_id: str):
        self.org_id = org_id
        self.session_id = session_id

        self.organization_details: Optional[OrganizationDetail] = (
            fetch_organization_details(org_id)
        )

        self.execute_sql_query_func = None
        self.nlto_sql_tool = None

        if self.organization_details:
            """Create execute_sql_query_func and nlto_sql_tool based on the organization details."""

            workgroup_name = (
                self.organization_details.redshift_workspace.redshift_work_space
            )
            database_name = self.organization_details.redshift_workspace.database_name

            self.execute_sql_query_func = create_execute_sql_query_function(
                workgroup_name, database_name
            )

            self.nlto_sql_tool = create_nltosql_tool(
                self.organization_details.nltosql_tool_prompts
            )


class PublicSession(SessionState):
    """Session state for the public chat."""

    def __init__(self, org_id: str, session_id: str):
        super().__init__(org_id, session_id)
        self.support_graph = create_support_graph(org_id)


class PrivateSession(SessionState):
    """Session state for the private chat."""

    def __init__(self, org_id: str, session_id: str):
        super().__init__(org_id, session_id)
        self.insights_graph = create_insights_graph(org_id)
