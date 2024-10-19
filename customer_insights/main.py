import uuid
from langgraph.checkpoint.memory import MemorySaver

from graph import create_insights_graph
from utils import visualize_graph

memory = MemorySaver()

graph = create_insights_graph(memory=memory)


# Visualize Graph
visualize_graph(graph)

thread_id = str(uuid.uuid4())

config = {"configurable": {"thread_id": thread_id}}

while True:
    user_input = input("User: ")

    if user_input in ["q", "quit", "exit"]:
        print("goodbye")
        break

    for event in graph.stream(
        {"messages": ("user", user_input)}, config, stream_mode="values"
    ):
        event["messages"][-1].pretty_print()
