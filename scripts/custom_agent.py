import uuid

from langchain_core.runnables import RunnableConfig

from graphs.custom_agent.graph import create_custom_agent_graph
from session.session import CustomAgentSession

session_state = CustomAgentSession(
    org_id="66158fe71bfe10b58cb23eea", session_id="1", agent_name="RAG Agent"
)

graph = create_custom_agent_graph(session_state)

config = RunnableConfig(
    configurable={
        "thread_id": str(uuid.uuid4()),
        "session_state": session_state,
    }
)

while True:
    user_input = input("User: ")

    if user_input in ["q", "quit", "exit"]:
        break

    for event in graph.stream(
        {"messages": [("user", user_input)], "org_id": session_state.org_id},
        config,
        stream_mode="values",
    ):
        event["messages"][-1].pretty_print()


with open("graphs/custom_agent/graph.png", "wb") as f:
    f.write(graph.get_graph(xray=True).draw_mermaid_png())
