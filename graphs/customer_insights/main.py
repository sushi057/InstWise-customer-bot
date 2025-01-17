import uuid
from langgraph.checkpoint.memory import MemorySaver

from graphs.customer_insights.graph import create_insights_graph
from graphs.customer_insights.helpers import visualize_graph

memory = MemorySaver()
graph = create_insights_graph(org_id="66158fe71bfe10b58cb23eea", memory=memory)

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
