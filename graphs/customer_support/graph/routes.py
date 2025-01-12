from typing import Literal

from langgraph.prebuilt import tools_condition
from langgraph.graph import END
from langchain_core.runnables import RunnableConfig

from graphs.customer_support.states.state import GraphState
from graphs.customer_support.tools.agent_routes import ToSolutionAgent, ToFollowUpAgent


def route_primary_assistant(
    state: GraphState,
) -> Literal["primary_assistant_tools", "solution_agent", "followup_agent", "__end__"]:
    route = tools_condition(state)

    if route == END:
        return "__end__"
    elif route == "tools":
        if state["messages"][-1].tool_calls[0]["name"] == ToSolutionAgent.name:
            return "solution_agent"
        elif state["messages"][-1].tool_calls[0]["name"] == ToFollowUpAgent.name:
            return "followup_agent"
        else:
            return "primary_assistant_tools"


def route_solution_agent(
    state: GraphState,
) -> Literal["solution_agent_tools", "__end__"]:
    route = tools_condition(state)

    if route == END:
        return "__end__"
    elif route == "tools":
        return "solution_agent_tools"


def route_followup_agent(
    state: GraphState,
) -> Literal["followup_agent_tools", "__end__"]:
    route = tools_condition(state)
    if route == "tools":
        return "followup_agent_tools"
    else:
        return "__end__"


def route_entry_point(state: GraphState, config: RunnableConfig):
    """
    Set entry points based on wether the customer has been verified.
    """
    if state.get("customer_info"):
        return "primary_assistant"
    else:
        return "fetch_user_info"
