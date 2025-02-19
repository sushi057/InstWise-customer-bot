import logging
from graphs.task_agent.agents import create_task_agent
from graphs.task_agent.models import Task

logger = logging.getLogger(__name__)

task_agent = create_task_agent(
    Task(org_id="66158fe71bfe10b58cb23eea", task_name="Negative Sentiment")
)

logger.info(f"Task Agent created successfully {task_agent}")
print(task_agent.invoke({}))


#
# /task_agent/feature_adoption
# org_id: 66158fe71bfe10b58cb23eea
#
# Optional
#     customer_id
#     csm_owner_id
#
