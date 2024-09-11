import uuid
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition
from langchain_core.messages import BaseMessage

from states.state import State
from models.openai_model import get_openai_model
from tools.tools import (
    fetch_customer_info,
    lookup_activity,
    clarify_issue,
    investigate_issue,
    provide_solution,
    personalized_follow_up,
    offer_additional_support,
    log_activity,
    create_tool_node_with_fallback,
    handle_tool_error,
    _print_event,
)
from prompts.prompts import primary_assistant_prompt

from fastapi import FastAPI

app = FastAPI()


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


llm = get_openai_model()

tools = [
    fetch_customer_info,
    lookup_activity,
    clarify_issue,
    investigate_issue,
    provide_solution,
    personalized_follow_up,
    offer_additional_support,
    log_activity,
]

assistant_runnable = primary_assistant_prompt | llm.bind_tools(tools)

builder = StateGraph(State)

builder.add_node("assistant", Assistant(assistant_runnable))
builder.add_node("tools", create_tool_node_with_fallback(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# thread_id = str(uuid.uuid4())
thread_id = "1234"

config = {
    "configurable": {
        "thread_id": thread_id,
    }
}

# while True:
#     user_input = input("User: ")

#     if user_input.lower() in ["quit", "exit", "q"]:
#         print("Goodbye!")
#         break
#     for event in graph.stream({"messages": [("user", user_input)]}, config):
#         for value in event.values():
#             if isinstance(value["messages"], BaseMessage):
#                 print("Assistant:", value["messages"].content + "\n")


@app.get("/")
async def root():
    return {"message": "Hello world"}


# @app.get("/ask")
# async def ask_support(query: str):
#     async for event in graph.stream({"messages": [("user", query)]}, config):
#         for value in await event.values():
#             if isinstance(value["messages"], BaseMessage):
#                 return {"message": value["messages"].content}
#         # event["messages"][-1].pretty_print()
#         # return {"message": event["messages"][-1].content}


@app.get("/ask")
async def ask_support(query: str):
    messages = []
    async for event in graph.astream(
        {"messages": [("user", query)]}, config, stream_mode="values"
    ):
        event["messages"][-1].pretty_print()
        messages.append(event["messages"][-1].content)
        # return {"message": event["messages"][-1].content}
    return {"message": messages[-1]}
