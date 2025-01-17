import os
import requests
from typing import Optional, Literal
from dotenv import load_dotenv
from pydantic import EmailStr
from fastapi import FastAPI
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
# from langgraph.errors import GraphRecursionError

from routes import customer, outreach
from config.config import get_customer_info
from graphs.customer_support.graph.graph import create_support_graph
from graphs.customer_support.helpers.helpers import get_session_id
from graphs.customer_insights.graph import create_insights_graph

load_dotenv()
rag_api_url = os.getenv("RAG_API_URL")
rag_api_headers = {"X-API-KEY": f"{os.getenv('X_API_KEY')}"}


app = FastAPI()

# Include router
app.include_router(customer.router, prefix="/customer", tags=["customer"])
app.include_router(outreach.router, prefix="/outreach", tags=["outreach"])

session_graph_cache = {"session_id": "", "graph": None, "customer_id": ""}
customer_info = {"customer_info": None}


@app.get("/", status_code=200)
async def root():
    return {"message": "Instwise Customer Support"}


@app.get("/ask")
async def ask_support(
    query: str,
    user_email: EmailStr,  # Optional
    org_id: str,
    api_type: Literal["support", "insights"],
    session_id: Optional[str] = None,
    customer_id: Optional[str] = None,  # 0000
):
    """
    Private Chat API for customer support and customer insights.
    The customer_id is 0000 by default for internal users.
    """

    # Improve this session_id cache design
    if session_graph_cache["session_id"] != session_id:
        session_graph_cache["session_id"] = get_session_id()
        new_memory = MemorySaver()

        # Generate new graph based on the API type
        if api_type == "insights":
            session_graph_cache["graph"] = create_insights_graph(
                org_id=org_id, memory=new_memory
            )

    if api_type == "support":
        # session_graph_cache["graph"] = create_support_graph(
        #     org_id=org_id, memory=new_memory
        # )
        response = requests.get(
            rag_api_url,
            headers=rag_api_headers,
            params={
                "query": query,
                "company_id": org_id,
            },
        )
        return {
            "message": response.json()["results"]["answer"],
            "session_id": session_graph_cache["session_id"],
            "customer_id": customer_id,
        }
    graph = session_graph_cache["graph"]

    config = {
        "configurable": {
            "thread_id": session_graph_cache["session_id"],
            "customer_email": user_email,
            "org_id": org_id,
            "internal_user": True,
        }
    }

    messages = []

    try:
        async for event in graph.astream(
            {"messages": [("user", query)]}, config, stream_mode="values"
        ):
            event["messages"][-1].pretty_print()
            messages.append(event["messages"][-1].content)
    # except GraphRecursionError:
    #     return {
    #         "message": "Graph Recursion Error, Please try again.",
    #         "session_id": session_id,
    #         "customer_id": customer_info.get("customer_id"),
    #     }
    except Exception as e:
        return {"error": str(e), "session_id": session_id}

    return {
        "message": messages[-1],
        "session_id": session_graph_cache["session_id"],
        "customer_id": get_customer_info().get("customer_id"),
    }


@app.get("/public/ask")
async def ask_public_chat(
    query: str,
    org_id: str,
    session_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    user_email: Optional[EmailStr] = None,
):
    """
    Chat API for external customers. This API only supports customer_support workflow.
    Initially, user_email is empty. The customer_id is other than 0000.
    """

    # Checks for a new session and creates a new graph
    if session_graph_cache["session_id"] != session_id:
        session_graph_cache["session_id"] = session_id
        session_graph_cache["graph"] = create_support_graph(org_id=org_id)

    graph = session_graph_cache["graph"]

    config = RunnableConfig(
        configurable={
            "thread_id": session_graph_cache["session_id"],
            "user_email": user_email,
            "org_id": org_id,
            "internal_user": False,
        }
    )

    messages = []
    try:
        async for event in graph.astream(
            {
                "messages": [("user", query)],
            },
            config,
            stream_mode="values",
        ):
            event["messages"][-1].pretty_print()
            messages.append(event["messages"][-1].content)
    except Exception as e:
        return {"error": str(e), "session_id": session_id}

    return {
        "message": messages[-1],
        "session_id": session_graph_cache["session_id"],
        "customer_id": get_customer_info().get("customer_id"),
        "user_email": get_customer_info().get("customer_email"),
    }
