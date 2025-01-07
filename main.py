from typing import Optional, Literal

import uvicorn
from pydantic import EmailStr
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import GraphRecursionError

from routes import customer, outreach
from config.config import get_customer_id
from graphs.customer_support.graph.graph import create_graph
from graphs.customer_support.utils.utils import get_session_id
from graphs.customer_insights.graph import create_insights_graph

app = FastAPI()

# Include router
app.include_router(customer.router, prefix="/customer", tags=["customer"])
app.include_router(outreach.router, prefix="/outreach", tags=["outreach"])

session_graph_cache = {"session_id": "", "graph": None, "customer_id": ""}

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
    user_email: EmailStr,  # Optional
    org_id: str,
    api_type=Literal["insights", "support"],
    session_id: Optional[str] = None,
    customer_id: Optional[str] = None,  # from query_database tool
):
    if not session_id:
        new_session_id = get_session_id()

    if session_graph_cache["session_id"] != session_id:
        session_graph_cache["session_id"] = new_session_id
        new_memory = MemorySaver()

        # Check API type
        if api_type == "support":
            session_graph_cache["graph"] = create_graph(
                org_id=org_id, memory=new_memory
            )
        elif api_type == "insights":
            session_graph_cache["graph"] = create_insights_graph(memory=new_memory)

    graph = session_graph_cache["graph"]

    config = {
        "configurable": {
            "thread_id": session_id,
            "user_email": user_email,
            "customer_id": customer_id,
            "token": session_graph_cache["session_id"] + "_" + org_id,
        }
    }

    messages = []
    try:
        async for event in graph.astream(
            {"messages": [("user", query)]}, config, stream_mode="values"
        ):
            event["messages"][-1].pretty_print()
            messages.append(event["messages"][-1].content)
    except GraphRecursionError:
        return {
            "message": "Graph Recursion Error, Please try again.",
            "session_id": session_id,
            "customer_id": get_customer_id(),
        }
    except Exception as e:
        return {"error": str(e), "session_id": session_id}

    return {
        "message": PlainTextResponse(messages[-1]),
        "session_id": session_id,
        "customer_id": get_customer_id(),
    }


@app.get("/public/ask")
async def ask_public_chat(
    query: str,
    org_id: str,
    # customer_id: Optional[str],
    session_id: Optional[str] = None,
    # user_email: Optional[EmailStr],
):
    """
    Chat API for public customers.
    This API only has customer_support agent.
    """

    # Check if new session and create a new graph with new memory
    if not session_id:
        session_id = get_session_id()
        session_graph_cache["session_id"] = session_id
        new_memory = MemorySaver()

        session_graph_cache["graph"] = create_graph(org_id=org_id, memory=new_memory)

    graph = session_graph_cache["graph"]

    config = RunnableConfig(
        configurable={
            "thread_id": session_id,
        }
    )

    messages = []
    try:
        async for event in graph.astream(
            {"messages": [("user", query)]},
            config,
            stream_mode="values",
        ):
            event["messages"][-1].pretty_print()
            messages.append(event["messages"][-1].content)
    except GraphRecursionError:
        return {
            "message": "Graph Recursion Error, Please try again.",
            "session_id": session_id,
            "customer_id": get_customer_id(),
        }
    except Exception as e:
        return {"error": str(e), "session_id": session_id}

    return {
        "message": PlainTextResponse(messages[-1]),
        "session_id": session_id,
        "customer_id": get_customer_id(),
        "user_email": None,
    }
