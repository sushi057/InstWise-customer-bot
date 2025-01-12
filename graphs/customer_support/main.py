import uuid
from langgraph.checkpoint.memory import MemorySaver

from graphs.customer_support.graph.graph import create_graph
from graphs.customer_support.utils.utils import visualize_graph

memory = MemorySaver()

graph = create_graph(org_id="123", memory=memory)

visualize_graph(graph)

thread_id = str(uuid.uuid4())


config = {
    "configurable": {
        "thread_id": str(uuid.uuid4()),
        # "user_email": "sarah@test.com",
        "customer_id": "123",
        "internal_user": False,
    }
}

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
