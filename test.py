import uuid

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable, RunnableConfig

from agents.agents import (
    greeting_agent_runnable,
    assistant_runnable,
    investigation_runnable,
    route_primary_assistant,
    solution_runnable,
    recommendation_runnable,
    log_runnable,
    upsell_runnable,
    survey_runnable,
    route_log_agent,
    route_greeting_agent,
    route_investigation_agent,
    route_solution_agent,
    route_recommendation_agent,
    route_log_agent,
    route_upsell_agent,
    greeting_tools,
    investigation_tools,
    solution_tools,
    recommendation_tools,
    log_tools,
    upsell_tools,
)

from states.state import State
from tools.tools import create_tool_node_with_fallback


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            configuration = config.get("configuration", {})
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


builder = StateGraph(State)

builder.add_node("greeting_agent", Assistant(greeting_agent_runnable))
builder.add_node("primary_assistant", Assistant(assistant_runnable))
builder.add_node("investigation_agent", Assistant(investigation_runnable))
builder.add_node("solution_agent", Assistant(solution_runnable))
builder.add_node("recommendation_agent", Assistant(recommendation_runnable))
builder.add_node("log_agent", Assistant(log_runnable))
builder.add_node("upsell_agent", Assistant(upsell_runnable))
builder.add_node("survey_agent", Assistant(survey_runnable))

builder.add_node("greeting_agent_tools", create_tool_node_with_fallback(greeting_tools))
builder.add_node(
    "investigation_agent_tools", create_tool_node_with_fallback(investigation_tools)
)
builder.add_node("solution_agent_tools", create_tool_node_with_fallback(solution_tools))
builder.add_node(
    "recommendation_agent_tools", create_tool_node_with_fallback(recommendation_tools)
)
builder.add_node("log_agent_tools", create_tool_node_with_fallback(log_tools))
builder.add_node("upsell_agent_tools", create_tool_node_with_fallback(upsell_tools))


builder.add_edge(START, "greeting_agent")
builder.add_edge("greeting_agent", "primary_assistant")
builder.add_conditional_edges(
    "primary_assistant",
    route_primary_assistant,
    {
        "investigation_agent": "investigation_agent",
        "solution_agent": "solution_agent",
        "recommendation_agent": "recommendation_agent",
        "log_agent": "log_agent",
        "upsell_agent": "upsell_agent",
        "survey_agent": "survey_agent",
        END: END,
    },
)
builder.add_edge("survey_agent", END)

# builder.add_edge("greeting_agent", "greeting_agent_tools")
builder.add_conditional_edges(
    "greeting_agent",
    route_greeting_agent,
    {"greeting_agent_tools": "greeting_agent_tools"},
)
builder.add_edge("greeting_agent_tools", "greeting_agent")
builder.add_conditional_edges("investigation_agent", route_investigation_agent)
builder.add_edge("investigation_agent_tools", "investigation_agent")
builder.add_conditional_edges("solution_agent", route_solution_agent)
builder.add_edge("solution_agent_tools", "solution_agent")
builder.add_conditional_edges("recommendation_agent", route_recommendation_agent)
builder.add_edge("recommendation_agent_tools", "recommendation_agent")
builder.add_conditional_edges("log_agent", route_log_agent)
builder.add_edge("log_agent_tools", "log_agent")
builder.add_conditional_edges("upsell_agent", route_upsell_agent)
builder.add_edge("upsell_agent_tools", "upsell_agent")


graph = builder.compile()

# Visualize graph
with open("graph_v0.2.png", "wb") as f:
    f.write(graph.get_graph(xray=True).draw_mermaid_png())

# Conversation
thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id, "user_email": "sarah@test.com"}}

while True:
    user_input = input("User: ")

    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break

    for event in graph.stream({"messages": [("user", user_input)]}, config):
        for value in event.values():
            if isinstance(value["messages"], BaseMessage):
                print("Assistant:", value["messages"].content + "\n")
