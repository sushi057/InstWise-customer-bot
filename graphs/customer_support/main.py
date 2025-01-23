import uuid
from langchain_core.runnables import RunnableConfig

from graphs.customer_support.graph.graph import create_support_graph
from graphs.customer_support.helpers.helpers import visualize_graph

thread_id = str(uuid.uuid4())
config = RunnableConfig(
    configurable={
        "thread_id": str(uuid.uuid4()),
        "org_id": "66158fe71bfe10b58cb23eea",
        "internal_user": False,
    }
)

graph = create_support_graph("66158fe71bfe10b58cb23eea")
visualize_graph(graph)

while True:
    user_input = input("User: ")

    if user_input in ["q", "quit", "exit"]:
        break

    for event in graph.stream(
        {"messages": ("user", user_input)}, config, stream_mode="values"
    ):
        event["messages"][-1].pretty_print()

if __name__ == "__main__":
    print("From graphs/customer_support/main.py")
