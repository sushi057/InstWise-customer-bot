import uuid
from langgraph.checkpoint.memory import MemorySaver

from graph.graph import create_graph
from utils.utils import visualize_graph

memory = MemorySaver()

graph = create_graph(org_id="123", memory=memory)
visualize_graph(graph)

thread_id = str(uuid.uuid4())


config = {
    "configurable": {
        "thread_id": str(uuid.uuid4()),
        # "user_email": "sarah@test.com",
        "customer_id": "123",
        "token": "1235" + "_" + "66e534d37a7f6e9808c7b921",
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
