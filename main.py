import os
from typing import Optional
import uuid
import requests
from fastapi import Depends, FastAPI, HTTPException
from langgraph.checkpoint.memory import MemorySaver

from config import get_customer_id
from graph.graph import create_graph
from utils.utils import fetch_organization_details, get_session_id
from server.database import (
    retrieve_customer_by_email,
)

# Visualize graph

# with open("graph_v0.2.png", "wb") as f:
#     f.write(graph.get_graph(xray=True).draw_mermaid_png())

app = FastAPI()

memory = MemorySaver()

session_graph_cache = {"session_id": None, "graph": None, "customer_id": None}

session_object = {
    "session_id": None,
    "customer_id": None,
}


@app.get("/", status_code=200)
async def root():
    return {"message": "Instwise Customer Support"}


@app.get("/ask")
async def ask_support(
    query: str,
    user_email: str,
    org_id: str,
    session_id: Optional[str] = None,
    customer_id: Optional[str] = None,
):

    if not session_id:
        session_id = get_session_id()

    if session_graph_cache["session_id"] != session_id:
        session_graph_cache["session_id"] = session_id
        new_memory = MemorySaver()
        session_graph_cache["graph"] = create_graph(org_id=org_id, memory=new_memory)
        # Add user_info state here

    graph = session_graph_cache["graph"]

    with open("graph_v0.2.png", "wb") as f:
        f.write(graph.get_graph(xray=True).draw_mermaid_png())

    config = {
        "configurable": {
            "thread_id": session_id,
            "user_email": user_email,
            "customer_id": customer_id,
        }
    }

    messages = []
    try:
        async for event in graph.astream(
            {"messages": [("user", query)]}, config, stream_mode="values"
        ):
            event["messages"][-1].pretty_print()
            messages.append(event["messages"][-1].content)
            # return {"message": event["messages"][-1].content}
    except Exception as e:
        return {"error": str(e), "session_id": session_id}

    return {
        "message": messages[-1],
        "session_id": session_id,
        "customer_id": get_customer_id(),
    }
