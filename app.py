import uuid
import chainlit as cl
from graph.graph import create_graph
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

graph = create_graph(org_id="66158fe71bfe10b58cb23eea", memory=memory)

thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id, "user_email": "david@test.com"}}


@cl.on_message
async def main(query: str):
    messages = []
    async for event in graph.astream(
        {"messages": [("user", query.content)]}, config, stream_mode="values"
    ):
        event["messages"][-1].pretty_print()
        messages.append(event["messages"][-1].content)
    await cl.Message(content=messages[-1]).send()
