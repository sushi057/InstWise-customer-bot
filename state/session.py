from typing import cast

from graphs.customer_insights.graph import create_insights_graph
from graphs.customer_insights.models import InternalWorkflowPrompts
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

        self.org_details: OrganizationDetail = fetch_organization_details(org_id)

        self.customer_info = None

        # self.execute_sql_query_func = None
        # self.nltosql_tool = None
        # self.abstract_query_chain = None

        if self.org_details:
            """Create execute_sql_query_func and nlto_sql_tool based on the organization details."""

            workgroup_name = self.org_details.redshift_config.redshift_work_space
            database_name = self.org_details.redshift_config.database_name

            self.execute_sql_query_func = create_execute_sql_query_function(
                workgroup_name, database_name
            )

            self.nltosql_tool, self.abstract_query_chain = create_nltosql_tool(
                prompts=self.org_details.nltosql_tool_prompts.model_dump(),
                redshift_config=self.org_details.redshift_config.model_dump(),
            )

    def set_customer_info(self, *, customer_id: str, customer_email: str):
        self.customer_info = {"id": customer_id, "email": customer_email}

    def get_support_workflow_prompts(self):
        return self.org_details.support_workflow_prompts.model_dump()

    def get_nltosql_tool_prompts(self) -> InternalWorkflowPrompts:
        return cast(
            InternalWorkflowPrompts, self.org_details.nltosql_tool_prompts.model_dump()
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
