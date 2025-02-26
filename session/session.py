from session.session_base import SessionState


class PublicSession(SessionState):
    """Session state for the public chat."""

    def __init__(self, org_id: str, session_id: str):
        super().__init__(org_id, session_id)

        from graphs.customer_support.graph.graph import create_support_graph

        self.support_graph = create_support_graph(self)
        print("Created support graph")


class PrivateSession(SessionState):
    """Session state for the private chat."""

    def __init__(self, org_id: str, session_id: str):
        super().__init__(org_id, session_id)

        from graphs.customer_insights.graph import create_insights_graph

        self.insights_graph = create_insights_graph(self)
        print("Created insights graph")


class TaskSession(SessionState):
    """Session state for the task agent chat."""

    def __init__(self, org_id: str, session_id: str, task_name):
        super().__init__(org_id, session_id)

        from graphs.task_agent.agents import create_task_agent
        from graphs.task_agent.helpers import get_task_agent_details
        from graphs.task_agent.models import Task

        self.task = Task(org_id=org_id, task_name=task_name)
        self.task_details = get_task_agent_details(self.task)
        self.task_agent_graph = create_task_agent(self)
