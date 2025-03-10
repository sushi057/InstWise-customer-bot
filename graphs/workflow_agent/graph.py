import os

import requests
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver

from graphs.workflow_agent.agents import create_agents

load_dotenv()

organization_token = os.getenv("ORGANIZATION_TOKEN")


def create_graph():
    """Create a graph for the workflow agent.

    The nodes for this graph will be a primary assistant with multiple tasks(task_agents).
    """
    # with open(file_path) as f:
    #     agent_details = json.load(f)

    agent_details_url = f"https://api-assistant.instwise.app/api/v1/organization/agent?token={organization_token}&email=bhattachas@hotmail.com"

    agent_details = requests.get(agent_details_url).json()

    primary_assistant = create_agents(agent_details["data"][-1])

    checkpointer = InMemorySaver()

    graph = primary_assistant.compile(checkpointer=checkpointer)

    return graph
