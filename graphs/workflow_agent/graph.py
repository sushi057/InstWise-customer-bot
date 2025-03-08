import json
from pathlib import Path

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from graphs.workflow_agent.agents import create_agents

file_path = Path(__file__).parent / "data/onboarding_agent.json"


def create_graph():
    """Create a graph for the workflow agent.

    The nodes for this graph will be a primary assistant with multiple tasks(task_agents).
    """
    with open(file_path) as f:
        agent_details = json.load(f)

    primary_assistant = create_agents(agent_details)

    checkpointer = InMemorySaver()
    store = InMemoryStore()

    graph = primary_assistant.compile(checkpointer=checkpointer)

    return graph
