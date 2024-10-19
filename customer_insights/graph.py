from typing import Literal

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


from customer_insights.state import AgentStateGraph
from customer_insights.agents import (
    fetch_user_info,
    query_agent,
    crm_agent,
    crm_agent_tools,
    csm_agent,
    helpdesk_agent,
    helpdesk_agent_tools,
    chatdata_agent,
    insights_agent,
)
from customer_insights.utils import create_tool_node_with_fallback


def route_entry_point(state: AgentStateGraph):
    if "user_info" in state:
        return "query_agent"
    else:
        return "fetch_user_info"


def route_query_agent(state: AgentStateGraph):
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return "__end__"
    elif last_message.tool_calls[0]["name"] == "ToCSMAgent":
        return "csm_agent"
    elif last_message.tool_calls[0]["name"] == "ToCRMAgent":
        return "crm_agent"
    elif last_message.tool_calls[0]["name"] == "ToHelpDeskAgent":
        return "helpdesk_agent"
    elif last_message.tool_calls[0]["name"] == "ToChatDataAgent":
        return "chatdata_agent"


def route_crm_agent(
    state: AgentStateGraph,
) -> Literal["crm_agent_tools", "insights_agent"]:
    tool_calls = state["messages"][-1].tool_calls
    if not tool_calls:
        return "insights_agent"
    return "crm_agent_tools"


def route_helpdesk_agent(
    state: AgentStateGraph,
) -> Literal["helpdesk_agent_tools", "insights_agent"]:
    tool_calls = state["messages"][-1].tool_calls
    if not tool_calls:
        return "insights_agent"
    return "helpdesk_agent_tools"


def create_insights_graph(memory):
    graph_builder = StateGraph(AgentStateGraph)

    graph_builder.add_node("fetch_user_info", fetch_user_info)
    graph_builder.add_node("query_agent", query_agent)
    graph_builder.add_node("crm_agent", crm_agent)
    graph_builder.add_node(
        "crm_agent_tools", create_tool_node_with_fallback(crm_agent_tools)
    )
    graph_builder.add_node("csm_agent", csm_agent)
    graph_builder.add_node("helpdesk_agent", helpdesk_agent)
    graph_builder.add_node(
        "helpdesk_agent_tools", create_tool_node_with_fallback(helpdesk_agent_tools)
    )
    graph_builder.add_node("chatdata_agent", chatdata_agent)
    graph_builder.add_node("insights_agent", insights_agent)

    graph_builder.set_conditional_entry_point(
        route_entry_point,
        {"fetch_user_info": "fetch_user_info", "query_agent": "query_agent"},
    )
    graph_builder.add_edge("fetch_user_info", "query_agent")
    graph_builder.add_conditional_edges(
        "query_agent",
        route_query_agent,
        {
            "crm_agent": "crm_agent",
            "csm_agent": "csm_agent",
            "helpdesk_agent": "helpdesk_agent",
            "chatdata_agent": "chatdata_agent",
            "__end__": END,
        },
    )

    graph_builder.add_conditional_edges(
        "crm_agent",
        route_crm_agent,
        {"crm_agent_tools": "crm_agent_tools", "insights_agent": "insights_agent"},
    )
    graph_builder.add_edge("crm_agent_tools", "crm_agent")

    graph_builder.add_conditional_edges(
        "helpdesk_agent",
        route_helpdesk_agent,
        {
            "helpdesk_agent_tools": "helpdesk_agent_tools",
            "insights_agent": "insights_agent",
        },
    )
    graph_builder.add_edge("helpdesk_agent_tools", "helpdesk_agent")

    graph_builder.add_edge("csm_agent", "insights_agent")
    graph_builder.add_edge("chatdata_agent", "insights_agent")
    graph_builder.add_edge("insights_agent", END)

    graph = graph_builder.compile(checkpointer=memory)

    return graph
