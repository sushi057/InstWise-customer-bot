import os
import uuid
import requests
from fastapi import Depends, FastAPI, HTTPException
from langgraph.checkpoint.memory import MemorySaver


from graph.graph import create_graph
from utils.utils import fetch_organization_details


# Visualize graph
# with open("graph_v0.2.png", "wb") as f:
#     f.write(graph.get_graph(xray=True).draw_mermaid_png())

# Conversation

thread_id = str(uuid.uuid4())

# config = {"configurable": {"thread_id": thread_id, "user_email": "david@test.com"}}

# while True:
#     user_input = input("User: ")

#     if user_input.lower() in ["quit", "exit", "q"]:
#         print("Goodbye!")
#         break

#     for event in graph.stream({"messages": [("user", user_input)]}, config):
#         for value in event.values():
#             if "user_info" in value:  # Need to fix this
#                 pass
#             elif isinstance(value["messages"], BaseMessage):
#                 print("Assistant:", value["messages"].content + "\n")

app = FastAPI()

memory = MemorySaver()


@app.get("/", status_code=200)
async def root():
    return {"message": "Hello world"}


@app.get("/ask")
async def ask_support(
    query: str,
    user_email: str,
    org_id: str,
):
    config = {"configurable": {"thread_id": thread_id, "user_email": user_email}}
    graph = create_graph(org_id=org_id, memory=memory)
    messages = []

    async for event in graph.astream(
        {"messages": [("user", query)]}, config, stream_mode="values"
    ):
        event["messages"][-1].pretty_print()
        messages.append(event["messages"][-1].content)
        # return {"message": event["messages"][-1].content}
    return {"message": messages[-1]}
