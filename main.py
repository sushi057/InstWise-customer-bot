from typing import Literal, Optional

from fastapi import Depends, FastAPI
from langchain_core.runnables import RunnableConfig
from pydantic import EmailStr

from routes import customer, outreach
from session.cache import (
    get_private_session_state,
    get_public_session_state,
    get_task_session_state,
)
from session.session import PrivateSession, PublicSession, TaskSession
from utils.helpers import call_rag_api

app = FastAPI()

# Include router
app.include_router(customer.router, prefix="/customer", tags=["customer"])
app.include_router(outreach.router, prefix="/outreach", tags=["outreach"])

customer_info = {"customer_info": None}


@app.get("/", status_code=200)
async def root():
    return {"message": "Instwise Customer Support"}


@app.get("/ask")
async def ask_support(
    query: str,
    user_email: EmailStr,  # Optional
    customer_id: str,  # 0000
    api_type: Literal["support", "insights"],
    session_state: PrivateSession = Depends(get_private_session_state),
):
    """Private Chat API for customer insights workflow."""

    session_id = session_state.session_id
    org_id = session_state.org_id

    try:
        if api_type == "support":
            rag_api_answer = call_rag_api.invoke({"query": query, "org_id": org_id})

            return {
                "message": rag_api_answer,
                "session_id": session_id,
                "customer_id": customer_id,
            }
        else:
            graph = session_state.insights_graph

            config = RunnableConfig(
                configurable={
                    "thread_id": session_id,
                    "session_state": session_state,
                }
            )

            messages = []

            # Compile all messages from the graph and send the last message
            # TODO: Implement streaming
            async for event in graph.astream(
                {"messages": [("user", query)]}, config, stream_mode="values"
            ):
                event["messages"][-1].pretty_print()
                messages.append(event["messages"][-1].content)

            return {
                "message": messages[-1],
                "session_id": session_id,
                "customer_id": customer_id,
            }

    except Exception as e:
        return {"message": f"Error: {str(e)}", "session_id": session_id}


@app.get("/public/ask")
async def ask_public_chat(
    query: str,
    user_email: Optional[str] = None,
    session_state: PublicSession = Depends(get_public_session_state),
):
    """
    Chat API for external customers. This API only supports customer_support workflow.
    Initially, user_email is empty.
    """

    session_id = session_state.session_id

    try:
        graph = session_state.support_graph

        config = RunnableConfig(
            configurable={
                "thread_id": session_id,
                "user_email": user_email,
                "session_state": session_state,
            }
        )

        messages = []
        async for event in graph.astream(
            {
                "messages": [("user", query)],
            },
            config,
            stream_mode="values",
        ):
            event["messages"][-1].pretty_print()
            messages.append(event["messages"][-1].content)

        return {
            "message": messages[-1],
            "session_id": session_id,
            "customer_id": session_state.customer_info.customer_id,
            "user_email": session_state.customer_info.customer_email,
        }

    except Exception as e:
        return {"message": f"Error {str(e)}", "session_id": session_id}


@app.post("/task-agent")
async def ask_task_agent(session_state: TaskSession = Depends(get_task_session_state)):
    """Task Agent API created based on the given task name."""
    task_agent = session_state.task_agent_graph
    response = task_agent.invoke({})
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
