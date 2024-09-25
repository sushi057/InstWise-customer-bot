from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.checkpoint.memory import MemorySaver


from agents.agents import (
    create_agents,
    route_primary_assistant,
    route_log_agent,
    route_investigation_agent,
    route_solution_agent,
    route_recommendation_agent,
    route_log_agent,
    route_upsell_agent,
    primary_assistant_tools,
    investigation_tools,
    solution_tools,
    recommendation_tools,
    log_tools,
    upsell_tools,
)

from states.state import State
from tools.tools import create_tool_node_with_fallback, fetch_user_info, _print_event
from utils.utils import create_entry_node, pop_dialog_state


def create_graph(org_id: str, memory):
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
                    messages = state["messages"] + [
                        ("user", "Respond with a real output")
                    ]
                    state = {**state, "messages": messages}
                else:
                    break

            return {"messages": result}

    builder = StateGraph(State)

    # def user_info(state: State):
    #     print("State: ", state)
    #     return {**state, "user_info": fetch_user_info.invoke({})}

    # builder.add_node("fetch_user_info", user_info)
    # builder.add_edge(START, "fetch_user_info")

    # Greeting Assistant

    # builder.add_edge(START, "greeting_agent")
    # builder.add_node("greeting_agent", Assistant(greeting_agent_runnable))
    # builder.add_node("greeting_agent_tools", create_tool_node_with_fallback(greeting_tools))
    # builder.add_edge("greeting_agent_tools", "greeting_agent")
    # builder.add_conditional_edges(
    #     "greeting_agent",
    #     route_greeting_agent,
    # )
    # builder.add_edge("greeting_agent", "primary_assistant")

    # Create agents
    agents = create_agents(org_id=org_id)

    # Investigation Agent

    builder.add_node(
        "enter_investigation_agent",
        create_entry_node("Investigation Agent", "investigation_agent"),
    )
    builder.add_node("investigation_agent", Assistant(agents["investigation_runnable"]))
    builder.add_edge("enter_investigation_agent", "investigation_agent")
    builder.add_node(
        "investigation_agent_tools", create_tool_node_with_fallback(investigation_tools)
    )
    builder.add_edge("investigation_agent_tools", "investigation_agent")
    builder.add_conditional_edges("investigation_agent", route_investigation_agent)

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

    # Recommendation Agent

    builder.add_node(
        "enter_recommendation_agent",
        create_entry_node("Recommendation Agent", "recommendation_agent"),
    )
    builder.add_node(
        "recommendation_agent", Assistant(agents["recommendation_runnable"])
    )
    builder.add_edge("enter_recommendation_agent", "recommendation_agent")
    builder.add_node(
        "recommendation_agent_tools",
        create_tool_node_with_fallback(recommendation_tools),
    )
    builder.add_conditional_edges("recommendation_agent", route_recommendation_agent)
    builder.add_edge("recommendation_agent_tools", "recommendation_agent")

    # Log Agent

    builder.add_node("enter_log_agent", create_entry_node("Log Agent", "log_agent"))
    builder.add_node("log_agent", Assistant(agents["log_runnable"]))
    builder.add_edge("enter_log_agent", "log_agent")
    builder.add_node("log_agent_tools", create_tool_node_with_fallback(log_tools))
    builder.add_edge("log_agent_tools", "log_agent")
    builder.add_conditional_edges("log_agent", route_log_agent)

    # Upsell Agent

    builder.add_node(
        "enter_upsell_agent", create_entry_node("Upsell Agent", "upsell_agent")
    )
    builder.add_node("upsell_agent", Assistant(agents["upsell_runnable"]))
    builder.add_edge("enter_upsell_agent", "upsell_agent")
    builder.add_node("upsell_agent_tools", create_tool_node_with_fallback(upsell_tools))
    builder.add_edge("upsell_agent_tools", "upsell_agent")
    builder.add_conditional_edges("upsell_agent", route_upsell_agent)

    # Survey Agent

    builder.add_node(
        "enter_survey_agent", create_entry_node("Survey Agent", "survey_agent")
    )
    builder.add_node("survey_agent", Assistant(agents["survey_runnable"]))
    builder.add_edge("enter_survey_agent", "survey_agent")
    builder.add_edge("survey_agent", END)

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
            "enter_investigation_agent": "enter_investigation_agent",
            "enter_solution_agent": "enter_solution_agent",
            "enter_recommendation_agent": "enter_recommendation_agent",
            "enter_log_agent": "enter_log_agent",
            "enter_upsell_agent": "enter_upsell_agent",
            "enter_survey_agent": "enter_survey_agent",
            "primary_assistant_tools": "primary_assistant_tools",
            END: END,
        },
    )

    builder.add_edge(START, "primary_assistant")

    builder.add_node("leave_skill", pop_dialog_state)
    builder.add_edge("leave_skill", "primary_assistant")

    graph = builder.compile(checkpointer=memory)

    return graph
