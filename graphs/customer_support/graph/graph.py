from langgraph.checkpoint.memory import MemorySaver

# from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph

from graphs.customer_support.agents.agents import create_agents
from graphs.customer_support.states.state import GraphState


from graphs.customer_support.graph.routes import (
    route_entry_point,
)
from graphs.customer_support.helpers.helpers import (
    create_tool_node_with_fallback,
)


def create_support_graph(org_id: str):
    """Create the customer support graph"""

    agents = create_agents(org_id=org_id)

    builder = StateGraph(GraphState)

    # Set conditional entry point based on customer verification
    builder.add_node("fetch_user_info", agents["fetch_user_info"])
    builder.set_conditional_entry_point(
        route_entry_point,
        {
            "fetch_user_info": "fetch_user_info",
            "primary_assistant": "primary_assistant",
            "followup_agent": "followup_agent",
            "solution_agent": "solution_agent",
        },
    )

    ## Primary Assistant
    builder.add_node("primary_assistant", agents["primary_assistant"])
    builder.add_node(
        "primary_assistant_tools",
        create_tool_node_with_fallback(agents["primary_assistant_tools"]),
    )
    builder.add_edge("primary_assistant_tools", "primary_assistant")

    ## Solution Agent
    builder.add_node("solution_agent", agents["solution_agent"])
    builder.add_node(
        "solution_agent_tools",
        create_tool_node_with_fallback(agents["solution_agent_tools"]),
    )
    builder.add_edge("solution_agent_tools", "solution_agent")
    # Follow-up Agent
    builder.add_node("followup_agent", agents["followup_agent"])
    builder.add_node(
        "followup_agent_tools",
        create_tool_node_with_fallback(agents["followup_agent_tools"]),
    )
    builder.add_edge("followup_agent_tools", "followup_agent")
    builder.add_node("human_node", agents["human_node"])

    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)

    return graph
