from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition

# from graphs.customer_insights.tools.tools import query_database
from graphs.customer_insights.state import AgentStateGraph
from graphs.customer_insights.agents import (
    create_internal_workflow_agents,
    # data_agent
)
from graphs.customer_insights.helpers import (
    create_tool_node_with_fallback,
)


def route_validation_agent(state: AgentStateGraph):
    response = state["messages"][-1].content
    if response == "True":
        return "insights_agent"
    else:
        return "data_agent"


def create_insights_graph(org_id: str, memory):
    graph_builder = StateGraph(AgentStateGraph)

    # Load agents
    agents = create_internal_workflow_agents(org_id=org_id)

    # Define nodes
    graph_builder.add_node("data_agent", agents["data_agent"])
    graph_builder.add_node(
        "tools", create_tool_node_with_fallback([agents["query_database"]])
    )

    # Define edges
    graph_builder.add_edge(START, "data_agent")
    graph_builder.add_conditional_edges(
        "data_agent",
        tools_condition,
        {
            "tools": "tools",
            "__end__": "__end__",
        },
    )
    graph_builder.add_edge("tools", "data_agent")
    graph_builder.add_edge("data_agent", END)

    # Add persistence memory
    graph = graph_builder.compile(checkpointer=memory)

    return graph
