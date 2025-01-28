from typing import cast
from langchain_openai import ChatOpenAI
from langgraph.graph.graph import CompiledGraph
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition
from langsmith import traceable

# from graphs.customer_insights.tools.tools import query_database
from graphs.customer_insights.state import AgentStateGraph
from graphs.customer_insights.agents import (
    RouterAgentOutput,
    create_internal_workflow_agents,
    # data_agent
)
from graphs.customer_insights.helpers import (
    create_tool_node_with_fallback,
)
from graphs.customer_insights.prompts import router_prompt_template
from graphs.customer_support.tools.zendesk import (
    create_zendesk_ticket_for_unresolved_issues,
)

llm_mini = ChatOpenAI(model="gpt-4o-mini")


# Define route function
@traceable(run_type="tool", name="Router Function")
def route_function(state: AgentStateGraph):
    """Route the user query to the appropriate agent."""

    # Only use the user's message for routing, when last agent isnt action or data agent
    router_runnable = router_prompt_template | llm_mini.with_structured_output(
        RouterAgentOutput
    )
    response = cast(
        RouterAgentOutput, router_runnable.invoke({"messages": state["messages"]})
    )
    print(
        f"""===========================================\n\nRouting to {response.route}"""
    )
    if response.route == "action_agent":  # type: ignore
        return "action_agent"
    elif response.route == "product_knowledge_agent":
        return "product_knowledge_agent"
    else:
        return "data_agent"


def create_insights_graph(org_id: str) -> CompiledGraph:
    """Create graph for insights workflow"""
    graph_builder = StateGraph(AgentStateGraph)

    # Load agents
    agents = create_internal_workflow_agents(org_id=org_id)

    # Define nodes
    graph_builder.add_node("data_agent", agents["data_agent"])
    graph_builder.add_node(
        "tools", create_tool_node_with_fallback([agents["query_database"]])
    )
    graph_builder.add_node("action_agent", agents["action_agent"])
    graph_builder.add_node(
        "action_agent_tools",
        create_tool_node_with_fallback([create_zendesk_ticket_for_unresolved_issues]),
    )
    graph_builder.add_node("product_knowledge_agent", agents["product_knowledge_agent"])

    # Define edges
    graph_builder.set_conditional_entry_point(
        # "router",
        route_function,
        {
            "data_agent": "data_agent",
            "action_agent": "action_agent",
            "product_knowledge_agent": "product_knowledge_agent",
        },
    )
    graph_builder.add_conditional_edges(
        "data_agent",
        tools_condition,
    )
    graph_builder.add_edge("tools", "data_agent")
    graph_builder.add_conditional_edges(
        "action_agent",
        tools_condition,
        {
            "tools": "action_agent_tools",
            "__end__": "__end__",
        },
    )
    graph_builder.add_edge("action_agent_tools", "action_agent")
    graph_builder.add_edge("product_knowledge_agent", "__end__")

    # Add persistence memory
    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)

    return graph
