import uuid

from langchain_core.runnables import RunnableConfig

from graphs.workflow_agent.graph import create_graph

graph = create_graph()

config = RunnableConfig(
    configurable={
        "thread_id": str(uuid.uuid4()),
    }
)

while True:
    user_input = input("User: ")

    if user_input in ["q", "quit", "exit"]:
        break

    for event in graph.stream(
        {"messages": ("user", user_input)}, config, stream_mode="values"
    ):
        event["messages"][-1].pretty_print()


with open("graphs/workflow_agent/graph.png", "wb") as f:
    graph = create_graph()
    f.write(graph.get_graph().draw_mermaid_png())
