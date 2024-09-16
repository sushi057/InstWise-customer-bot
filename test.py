from token import STAR
from typing import Literal
from IPython.display import Image, display

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition
from langchain_core.runnables import Runnable, RunnableConfig

from agents import (
    greeting_agent,
    primary_assistant,
    investigation_agent,
    solution_agent,
    recommendation_agent,
    log_agent,
    upsell_agent,
    survey_agent,
)

from agents.greeting_agent import greeting_tools
from agents.investigation_agent import investigation_tools
from agents.solution_agent import solution_tools
from agents.recommendation_agent import recommendation_tools
from agents.log_agent import log_tools
from agents.upsell_agent import upsell_tools

from states.state import State
from tools.tools import create_tool_node_with_fallback


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            configuration = config.get("configuration", {})
            thread_id = configuration.get("thread_id")
            state = {**state, "user_info": thread_id}
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

builder.add_node("greeting_agent", Assistant(greeting_agent))
builder.add_node("primary_assistant", Assistant(primary_assistant))
builder.add_node("investigation_agent", Assistant(investigation_agent))
builder.add_node("solution_agent", Assistant(solution_agent))
builder.add_node("recommendation_agent", Assistant(recommendation_agent))
builder.add_node("log_agent", Assistant(log_agent))
builder.add_node("upsell_agent", Assistant(upsell_agent))
builder.add_node("survey_agent", Assistant(survey_agent))

builder.add_node("tools", create_tool_node_with_fallback(greeting_tools))
# builder.add_node(
#     "investigation_agent_tools", create_tool_node_with_fallback(investigation_tools)
# )
# builder.add_node("solution_agent_tools", create_tool_node_with_fallback(solution_tools))
# builder.add_node(
#     "recommendation_agent_tools", create_tool_node_with_fallback(recommendation_tools)
# )
# builder.add_node("log_agent_tools", create_tool_node_with_fallback(log_tools))
# builder.add_node("upsell_agent_tools", create_tool_node_with_fallback(upsell_tools))

builder.add_edge(START, "greeting_agent")
builder.add_edge("greeting_agent", "primary_assistant")
builder.add_edge("primary_assistant", "investigation_agent")
builder.add_edge("primary_assistant", "solution_agent")
builder.add_edge("primary_assistant", "recommendation_agent")
builder.add_edge("primary_assistant", "log_agent")
builder.add_edge("primary_assistant", "upsell_agent")
builder.add_edge("primary_assistant", "survey_agent")
# builder.add_conditional_edges("solution_agent", "investigation_agent")
# builder.add_conditional_edges("solution_agent", "log_agent")

builder.add_edge("tools", "greeting_agent")
builder.add_conditional_edges("greeting_agent", tools_condition)
# builder.add_edge("investigation_agent_tools", "investigation_agent")
# builder.add_edge("solution_agent_tools", "solution_agent")
# builder.add_edge("recommendation_agent_tools", "recommendation_agent")
# builder.add_edge("log_agent_tools", "log_agent")
# builder.add_edge("upsell_agent_tools", "upsell_agent")

graph = builder.compile()

# Visualize graph
with open("graph_v0.2.png", "wb") as f:
    f.write(graph.get_graph(xray=True).draw_mermaid_png())
