from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import tools_condition

from graphs.customer_insights.agents import create_internal_workflow_agents
from graphs.customer_insights.helpers import create_tool_node_with_fallback
from graphs.customer_insights.state import AgentStateGraph
from session.session import SessionState


def create_insights_graph(session_state: SessionState) -> CompiledGraph:
    """Create graph for insights workflow"""

    graph_builder = StateGraph(AgentStateGraph)

    # Load agents
    data_agent, data_agent_tools = create_internal_workflow_agents(session_state)

    # Define nodes
    graph_builder.add_node("data_agent", data_agent)
    graph_builder.add_node("tools", create_tool_node_with_fallback(data_agent_tools))

    # Define edges
    graph_builder.add_edge(START, "data_agent")
    graph_builder.add_conditional_edges(
        "data_agent",
        tools_condition,
    )
    graph_builder.add_edge("tools", "data_agent")
    graph_builder.add_edge("data_agent", END)

    # Add persistence memory
    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)

    return graph
