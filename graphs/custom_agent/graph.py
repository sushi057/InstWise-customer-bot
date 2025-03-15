import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver

from graphs.custom_agent.agents import create_agents
from session.session import CustomAgentSession

load_dotenv()

organization_token = os.getenv("ORGANIZATION_TOKEN")


def create_custom_agent_graph(session_state: CustomAgentSession):
    """Create a graph for the workflow agent.

    The nodes for this graph will be a primary assistant with multiple tasks(task_agents).
    """

    # with open(str(Path.cwd()) + "/graphs/custom_agent/data.json") as f:
    #     data = json.load(f)

    primary_assistant = create_agents(session_state)

    checkpointer = InMemorySaver()
    graph = primary_assistant.compile(checkpointer=checkpointer)

    return graph
