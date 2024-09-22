from typing import Literal
import uuid

from langchain_core.messages import BaseMessage

from graph.graph import create_graph

graph = create_graph()
# Visualize graph
with open("graph_v0.2.png", "wb") as f:
    f.write(graph.get_graph(xray=True).draw_mermaid_png())

# Conversation

thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id, "user_email": "jim@test.com"}}

while True:
    user_input = input("User: ")

    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break

    for event in graph.stream({"messages": [("user", user_input)]}, config):
        for value in event.values():
            if "user_info" in value:  # Need to fix this
                pass
            elif isinstance(value["messages"], BaseMessage):
                print("Assistant:", value["messages"].content + "\n")
