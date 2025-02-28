import logging

from session.session import TaskSession

logger = logging.getLogger(__name__)
session_state = TaskSession("66158fe71bfe10b58cb23eea", "123", "Negative Sentiment")

task_agent = session_state.task_agent_graph

logger.info(f"Task Agent created successfully {task_agent}")
print(task_agent.invoke({}))
