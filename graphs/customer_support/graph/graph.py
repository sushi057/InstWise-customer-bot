from langgraph.checkpoint.memory import MemorySaver
# from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph

from graphs.customer_support.agents.agents import create_agents
from graphs.customer_support.states.state import GraphState
from graphs.customer_support.graph.routes import (
    route_entry_point,
    route_primary_assistant,
    route_solution_agent,
    route_followup_agent,
)
from graphs.customer_support.helpers.helpers import (
    create_tool_node_with_fallback,
)


def create_support_graph(org_id: str):
    """Create the customer support graph"""

    # Get organization_id from config and create agents
    # org_id = config.get("configurable").get("org_id")
    agents = create_agents(org_id=org_id)

    builder = StateGraph(GraphState)

    # Set conditional entry point based on customer verification
    builder.add_node("fetch_user_info", agents["fetch_user_info"])
    builder.set_conditional_entry_point(
        route_entry_point,
        {
            "fetch_user_info": "fetch_user_info",
            "primary_assistant": "primary_assistant",
        },
    )

    ## Primary Assistant
    builder.add_node("primary_assistant", agents["primary_assistant"])
    builder.add_node(
        "primary_assistant_tools",
        create_tool_node_with_fallback(agents["primary_assistant_tools"]),
    )
    builder.add_edge("primary_assistant_tools", "primary_assistant")
    builder.add_conditional_edges(
        "primary_assistant",
        route_primary_assistant,
        {
            "primary_assistant_tools": "primary_assistant_tools",
            "solution_agent": "solution_agent",
            "followup_agent": "followup_agent",
            "__end__": "__end__",
        },
    )

    ## Solution Agent
    builder.add_node("solution_agent", agents["solution_agent"])
    builder.add_node(
        "solution_agent_tools",
        create_tool_node_with_fallback(agents["solution_agent_tools"]),
    )
    builder.add_edge("solution_agent_tools", "solution_agent")
    builder.add_conditional_edges(
        "solution_agent",
        route_solution_agent,
        {
            "solution_agent_tools": "solution_agent_tools",
            "followup_agent": "followup_agent",
            "__end__": "__end__",
        },
    )

    ## Follow-up Agent
    builder.add_node("followup_agent", agents["followup_agent"])
    builder.add_node(
        "followup_agent_tools",
        create_tool_node_with_fallback(agents["followup_agent_tools"]),
    )
    builder.add_edge("followup_agent_tools", "followup_agent")
    builder.add_conditional_edges("followup_agent", route_followup_agent)

    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)

    return graph
