from typing import Optional
from typing import Literal

from fastapi import FastAPI
from langgraph.checkpoint.memory import MemorySaver

from config.config import get_customer_id
from customer_support.graph.graph import create_graph
from customer_support.utils.utils import get_session_id
from customer_insights.graph import create_insights_graph

app = FastAPI()


session_graph_cache = {"session_id": None, "graph": None, "customer_id": None}

session_object = {
    "session_id": None,
    "customer_id": None,
    "organization_id": None,
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
    api_type: str = Literal["insights", "support"],
):

    if not session_id:
        session_id = get_session_id()

    if session_graph_cache["session_id"] != session_id:
        session_graph_cache["session_id"] = session_id
        new_memory = MemorySaver()

        # Check API type
        if api_type == "support":
            session_graph_cache["graph"] = create_graph(
                org_id=org_id, memory=new_memory
            )
        elif api_type == "insights":
            session_graph_cache["graph"] = create_insights_graph(memory=new_memory)
        # Add user_info state here

    graph = session_graph_cache["graph"]

    config = {
        "configurable": {
            "thread_id": session_id,
            "user_email": user_email,
            "customer_id": customer_id,
            "token": session_id + "_" + org_id,
        }
    }

    messages = []
    try:
        async for event in graph.astream(
            {"messages": [("user", query)]}, config, stream_mode="values"
        ):
            event["messages"][-1].pretty_print()
            messages.append(event["messages"][-1].content)
    except Exception as e:
        return {"error": str(e), "session_id": session_id}

    return {
        "message": messages[-1],
        "session_id": session_id,
        "customer_id": get_customer_id(),
    }
