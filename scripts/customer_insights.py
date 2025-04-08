import uuid

from langchain_core.runnables import RunnableConfig

from graphs.customer_insights.helpers import visualize_graph
from session.session import PrivateSession

session_state = PrivateSession("66158fe71bfe10b58cb23eea", "123")
graph = session_state.insights_graph

visualize_graph(graph)

thread_id = str(uuid.uuid4())
config = RunnableConfig(configurable={"thread_id": thread_id})

while True:
    user_input = input("User: ")

    if user_input in ["q", "quit", "exit"]:
        print("goodbye")
        break

    for event in graph.stream(
        {"messages": ("user", user_input)},
        config,
        stream_mode="values",
    ):
        event["messages"][-1].pretty_print()
