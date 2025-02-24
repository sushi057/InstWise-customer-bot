from typing import Any, Literal, Optional

from fastapi import Depends, FastAPI, Header
from langchain_core.runnables import RunnableConfig
from langgraph.errors import (EmailStr, GraphRecursionError, from, import,
                              pydantic)

from config.config import CustomerInfo, get_customer_info, set_customer_info
from graphs.customer_insights.graph import create_insights_graph
from graphs.customer_support.graph.graph import create_support_graph
from graphs.customer_support.helpers.helpers import get_session_id
from graphs.task_agent.agents import create_task_agent
from graphs.task_agent.models import Task
from models.task_agent import AskTaskAgentRequest
from routes import customer, outreach
from state.session import SessionState
from utils.helpers import call_rag_api

app = FastAPI()

# Include router
app.include_router(customer.router, prefix="/customer", tags=["customer"])
app.include_router(outreach.router, prefix="/outreach", tags=["outreach"])

session_graph_cache = {"session_id": "", "graph": None, "customer_id": ""}
customer_info = {"customer_info": None}

_session_state_cache: dict[tuple[str, str], SessionState] = {}


async def get_session_state(
    org_id_header: str = Header(..., alias="org_id"),
    session_id_header: str = Header(..., alias="session_id"),
) -> SessionState:
    """Dependency to get or create a SessionState object for the current session."""

    session_id = session_id_header
    org_id = org_id_header
    cache_key = (org_id, session_id)

    if cache_key in _session_state_cache:
        print(
            f"SessionState found in cache for session_id: {session_id}, org_id: {org_id}"
        )
        return _session_state_cache[cache_key]
    else:
        new_session_state = SessionState(org_id=org_id, session_id=session_id)
        _session_state_cache[cache_key] = new_session_state

        print(
            f"New SessionState created for session_id: {session_id}, org_id: {org_id}"
        )

        return new_session_state


@app.get("/", status_code=200)
async def root():
    return {"message": "Instwise Customer Support"}


@app.get("/ask")
async def ask_support(
    query: str,
    user_email: EmailStr,  # Optional
    org_id: str,
    customer_id: str,  # 0000
    api_type: Literal["support", "insights"],
    session_id: Optional[str] = None,
    session_state: SessionState = Depends(get_session_state),
):
    """
    Private Chat API for customer support and customer insights.
    The customer_id is 0000 by default for internal users.
    """

    # Improve this session_id cache design
    if session_graph_cache["session_id"] != session_id:
        session_graph_cache["session_id"] = get_session_id()

        set_customer_info(
            customer_info=CustomerInfo(
                customer_id=customer_id, customer_email=user_email
            )
        )

        # Generate new graph based on the API type
        if api_type == "insights":
            session_graph_cache["graph"] = create_insights_graph(org_id=org_id)

    if api_type == "support":
        rag_api_answer = call_rag_api(query=query, org_id=org_id)
        return {
            "message": rag_api_answer,
            "session_id": session_graph_cache["session_id"],
            "customer_id": customer_id,
        }

    graph = session_graph_cache["graph"]

    config = RunnableConfig(
        configurable={
            "thread_id": session_graph_cache["session_id"],
            "customer_email": user_email,
            "org_id": org_id,
            "internal_user": True,
        }
    )

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
        "session_id": session_graph_cache["session_id"],
        "customer_id": get_customer_info().get("customer_id"),
    }


@app.get("/public/ask")
async def ask_public_chat(
    query: str,
    org_id: str,
    session_id: Optional[str] = None,
    user_email: Optional[str] = None,
):
    """
    Chat API for external customers. This API only supports customer_support workflow.
    Initially, user_email is empty. The customer_id is other than 0000.
    """

    # Checks for a new session and creates a new graph
    if session_graph_cache["session_id"] != session_id:
        session_graph_cache["session_id"] = session_id
        session_graph_cache["graph"] = create_support_graph(org_id=org_id)

        # Set global CustomerInfo to null for a new session
        set_customer_info(
            customer_info=CustomerInfo(customer_id=None, customer_email=None)
        )

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
    except GraphRecursionError:
        return {
            "message": "Graph Recursion Error, Please try again.",
            "session_id": session_id,
            "customer_id": customer_info.get("customer_id"),
        }
    except Exception as e:
        return {"error": str(e), "session_id": session_id}

    return {
        "message": messages[-1],
        "session_id": session_graph_cache["session_id"],
        "customer_id": get_customer_info().get("customer_id"),
        "user_email": get_customer_info().get("customer_email"),
    }


@app.post("/task-agent/{task_name}")
async def ask_task_agent(request: AskTaskAgentRequest):
    """
    Task Agent API created based on the given task name.

    """
    task_agent = create_task_agent(
        Task(org_id=request.org_id, task_name=request.task_name)
    )

    response = task_agent.invoke({})
    return response
