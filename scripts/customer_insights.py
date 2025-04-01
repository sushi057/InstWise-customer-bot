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

    for stream_mode, chunk in graph.stream(
        {"messages": ("user", user_input)}, config, stream_mode=["messages", "custom"]
    ):
        if stream_mode == "messages":
            message, metadata = chunk
            if metadata["langgraph_node"] != "tools":  # type: ignore
                if message.tool_calls:
                    print("Analyzing query")
                else:
                    print("Generating response")
                print(message.content, end="")
        else:
            print(chunk["status"])
