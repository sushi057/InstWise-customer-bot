from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition

from customer_insights.tools import text_to_sql
from customer_insights.state import AgentStateGraph
from customer_insights.agents import data_agent, validation_agent, insights_agent
from customer_insights.utils import create_tool_node_with_fallback


def route_validation_agent(state: AgentStateGraph):
    response = state["messages"][-1].content
    if response == "True":
        return "insights_agent"
    else:
        return "data_agent"


def create_insights_graph(memory):

    graph_builder = StateGraph(AgentStateGraph)

    # Define nodes
    graph_builder.add_node("data_agent", data_agent)
    graph_builder.add_node("tools", create_tool_node_with_fallback([text_to_sql]))
    # graph_builder.add_node("validation_agent", validation_agent)
    # graph_builder.add_node("insights_agent", insights_agent)

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
    # graph_builder.add_conditional_edges(
    #     "validation_agent",
    #     route_validation_agent,
    #     {"data_agent": "data_agent", "insights_agent": "insights_agent"},
    # )
    # graph_builder.add_edge("insights_agent", END)

    graph_builder.add_edge("data_agent", END)

    # Add persistence memory
    graph = graph_builder.compile(checkpointer=memory)

    return graph
