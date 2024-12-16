from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import tools_condition
from langchain_core.runnables import Runnable, RunnableConfig


from graphs.customer_support.agents.agents import (
    create_agents,
    primary_assistant_tools,
    solution_tools,
    followup_tools,
    log_tools,
    CompleteOrEscalate,
)
from graphs.customer_support.tools.agent_routes import (
    ToSolutionAgent,
    ToLogAgent,
    ToFollowUpAgent,
)
from graphs.customer_support.states.state import State
from graphs.customer_support.tools.tools import fetch_user_info
from graphs.customer_support.utils.utils import (
    create_entry_node,
    pop_dialog_state,
    create_tool_node_with_fallback,
)


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            configuration = config.get("configurable", {})
            thread_id = configuration.get("thread_id")
            state = {
                **state,
                "thread_id": thread_id,
            }
            result = self.runnable.invoke(state)

            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output")]
                state = {**state, "messages": messages}
            else:
                break

        return {"messages": result}


def get_user_info(state: State, config: RunnableConfig):
    configurable = config.get("configurable", {})
    user_email = configurable.get("user_email")
    customer_id = configurable.get("customer_id")

    # If customer_id is not 0000, then the API call is from public link
    if customer_id != "0000":
        return {
            **state,
            "user_info": {"user_id": customer_id, "user_email": user_email},
        }

    user_info = fetch_user_info(user_email)

    if not user_info:
        return {**state, "user_info": {"user_id": None, "user_email": None}}

    return {
        **state,
        "user_info": {
            "user_id": customer_id,
            "user_email": user_email,
            "name": f'{user_info["properties"]["firstname"]} {user_info["properties"]["lastname"]}',
            "pending_issues": user_info["properties"]["pending_issues"],
            "company": user_info["properties"]["company"],
        },
    }


def route_primary_assistant(
    state: State,
) -> Literal[
    "primary_assistant_tools",
    "enter_solution_agent",
    "enter_followup_agent",
    "enter_log_agent",
    "__end__",
]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
        if tool_calls[0]["name"] == ToSolutionAgent.__name__:
            return "enter_solution_agent"
        elif tool_calls[0]["name"] == ToLogAgent.__name__:
            return "enter_log_agent"
        elif tool_calls[0]["name"] == ToFollowUpAgent.__name__:
            return "enter_followup_agent"
        return "primary_assistant_tools"
    return ValueError("Invalid Route")


def route_solution_agent(
    state: State,
) -> Literal["solution_agent_tools", "leave_skill", "__end__"]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"

    return "solution_agent_tools"


def route_followup_agent(
    state: State,
) -> Literal["followup_agent_tools", "leave_skill", "__end__"]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"

    return "followup_agent_tools"


def route_log_agent(
    state: State,
) -> Literal["log_agent_tools", "leave_skill", "__end__"]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"

    return "log_agent_tools"


def route_entry_point(state: State):
    if "user_info" in state:
        return "primary_assistant"
    return "get_user_info"


def create_graph(org_id: str, memory):
    builder = StateGraph(State)

    builder.add_node("get_user_info", get_user_info)
    builder.set_conditional_entry_point(
        route_entry_point,
        {
            "get_user_info": "get_user_info",
            "primary_assistant": "primary_assistant",
        },
    )
    builder.add_edge("get_user_info", "primary_assistant")

    # Create agents
    agents = create_agents(org_id=org_id)

    # Primary Assistant

    builder.add_node("primary_assistant", Assistant(agents["assistant_runnable"]))
    builder.add_node(
        "primary_assistant_tools",
        create_tool_node_with_fallback(primary_assistant_tools),
    )
    builder.add_edge("primary_assistant_tools", "primary_assistant")
    builder.add_conditional_edges(
        "primary_assistant",
        route_primary_assistant,
        {
            "enter_solution_agent": "enter_solution_agent",
            "enter_followup_agent": "enter_followup_agent",
            "enter_log_agent": "enter_log_agent",
            "primary_assistant_tools": "primary_assistant_tools",
            END: END,
        },
    )

    # Solution Agent

    builder.add_node(
        "enter_solution_agent", create_entry_node("Solution Agent", "solution_agent")
    )
    builder
    builder.add_node("solution_agent", Assistant(agents["solution_runnable"]))
    builder.add_edge("enter_solution_agent", "solution_agent")
    builder.add_node(
        "solution_agent_tools", create_tool_node_with_fallback(solution_tools)
    )
    builder.add_edge("solution_agent_tools", "solution_agent")
    builder.add_conditional_edges("solution_agent", route_solution_agent)

    # Follow-up Agent
    builder.add_node(
        "enter_followup_agent", create_entry_node("Follow-up Agent", "followup_agent")
    )
    builder.add_node("followup_agent", Assistant(agents["followup_runnable"]))
    builder.add_edge("enter_followup_agent", "followup_agent")
    builder.add_node(
        "followup_agent_tools", create_tool_node_with_fallback(followup_tools)
    )
    builder.add_edge("followup_agent_tools", "followup_agent")
    builder.add_conditional_edges("followup_agent", route_followup_agent)
    # Log Agent

    builder.add_node("enter_log_agent", create_entry_node("Log Agent", "log_agent"))
    builder.add_node("log_agent", Assistant(agents["log_runnable"]))
    builder.add_edge("enter_log_agent", "log_agent")
    builder.add_node("log_agent_tools", create_tool_node_with_fallback(log_tools))
    builder.add_edge("log_agent_tools", "log_agent")
    builder.add_conditional_edges("log_agent", route_log_agent)

    builder.add_node("leave_skill", pop_dialog_state)
    builder.add_edge("leave_skill", "primary_assistant")

    graph = builder.compile(checkpointer=memory)

    return graph
