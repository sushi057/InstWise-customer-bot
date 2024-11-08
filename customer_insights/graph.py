from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition

from customer_insights.state import AgentStateGraph
from customer_insights.agents import (
    query_agent,
    query_agent_tools,
    customer_data_agent,
    tools,
    insights_agent,
)
from customer_insights.utils import create_tool_node_with_fallback


def route_query_agent(state: AgentStateGraph):
    """
    Decide wether to use tools
    """
    route = tools_condition(state["messages"])
    if route == "tools":
        return "query_agent_tools"
    return "customer_data_agent"


def create_insights_graph(memory):

    graph_builder = StateGraph(AgentStateGraph)

    # Define nodes
    graph_builder.add_node("query_agent", query_agent)
    graph_builder.add_node(
        "query_agent_tools", create_tool_node_with_fallback(query_agent_tools)
    )
    graph_builder.add_node("customer_data_agent", customer_data_agent)
    graph_builder.add_node("tools", create_tool_node_with_fallback(tools))
    # graph_builder.add_node("insights_agent", insights_agent)

    # Define edges
    graph_builder.add_edge(START, "query_agent")
    graph_builder.add_conditional_edges(
        "query_agent",
        route_query_agent,
        {
            "query_agent_tools": "query_agent_tools",
            "customer_data_agent": "customer_data_agent",
        },
    )
    graph_builder.add_edge("query_agent_tools", "query_agent")
    graph_builder.add_conditional_edges(
        "customer_data_agent",
        tools_condition,
        {
            "tools": "tools",
            "__end__": "__end__",
        },
    )
    graph_builder.add_edge("tools", "customer_data_agent")
    graph_builder.add_edge("customer_data_agent", END)
    # graph_builder.add_edge("insights_agent", END)

    graph = graph_builder.compile(checkpointer=memory)

    return graph
