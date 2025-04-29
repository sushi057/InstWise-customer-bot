import json
import logging
from typing import Literal, Optional, cast

from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from pydantic import EmailStr

from routes import customer, outreach
from session.cache import (
    get_custom_agent_session_state,
    get_private_session_state,
    get_public_session_state,
    get_task_session_state,
)
from session.session import (
    CustomAgentSession,
    PrivateSession,
    PublicSession,
    TaskSession,
)
from utils.helpers import call_rag_api
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(
    logging.WARNING
)  # Set httpx logging level to WARNING

app = FastAPI()

# Include router
app.include_router(customer.router, prefix="/customer", tags=["customer"])
app.include_router(outreach.router, prefix="/outreach", tags=["outreach"])

customer_info = {"customer_info": None}


@app.get("/", status_code=200)
async def root():
    logger.info("Root endpoint accessed.")
    return {"message": "Instwise Customer Support"}


@app.get("/ask")
async def ask_private_chat(
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

            logger.info(f"RAG API response: {rag_api_answer}")
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

            # Compile all messages from the graph and send the last message
            async def event_stream():
                full_message = ""
                async for stream_mode, chunk in graph.astream(
                    {"messages": [("user", query)]},
                    config,
                    stream_mode=["messages", "custom"],
                ):
                    content = None
                    status = "Generating insights"

                    if stream_mode == "messages":
                        message, metadata = chunk  # type: ignore
                        message = cast(AIMessage, message)
                        metadata = cast(dict, metadata)

                        if metadata["langgraph_node"] != "tools":
                            if message.tool_calls:
                                content = None
                                status = "Analyzing query"
                            elif message.content != "":
                                # Append content to full_message
                                full_message += message.content  # type: ignore

                                content = message.content
                                status = None
                    else:
                        content = None
                        status = chunk["status"]  # type: ignore

                    data = {
                        "message": content,
                        "status": status,
                        "session_id": session_id,
                        "customer_id": customer_id,
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                logger.info(f"Insights agent full message: {full_message}")

            return StreamingResponse(event_stream(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Error in private chat: {str(e)}")
        return {"message": f"Error: {str(e)}", "session_id": session_id}


@app.get("/ask/public")
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
        logger.error(f"Error in public chat: {str(e)}")
        return {"message": f"Error {str(e)}", "session_id": session_id}


@app.get("/ask/agent")
async def ask_custom_agent(
    agent_name: str,
    query: str,
    session_state: CustomAgentSession = Depends(get_custom_agent_session_state),
):
    """Custom Agent API created based on the given agent name."""
    session_id = session_state.session_id
    org_id = session_state.org_id

    config = RunnableConfig(
        configurable={
            "thread_id": session_id,
            "session_state": session_state,
        }
    )

    try:
        graph = session_state.graph

        async def event_stream():
            full_message = ""
            async for stream_mode, chunk in graph.astream(
                {"messages": [("user", query)], "org_id": org_id},
                config,
                stream_mode=["messages", "custom"],
            ):
                content = None
                status = "Processing"

                if stream_mode == "messages":
                    message, metadata = chunk  # type: ignore
                    message = cast(AIMessage, message)
                    metadata = cast(dict, metadata)

                    node_name = metadata.get("langgraph_node", "")

                    if "tools" not in node_name and node_name == "agent":
                        if hasattr(message, "tool_calls") and message.tool_calls:
                            # Extract child agent name from the tool call
                            if message.tool_calls[0]["name"] and message.tool_calls[0][
                                "name"
                            ].startswith("transfer_to_"):
                                child_agent = message.tool_calls[0]["name"].split(
                                    "transfer_to_"
                                )[-1]
                            else:
                                child_agent = None

                            content = None
                            if child_agent:
                                status = f"Moving to {child_agent}"
                            else:
                                status = "Analyzing query"
                        elif message.content != "":
                            # Append content to full_message
                            full_message += message.content  # type: ignore

                            content = message.content
                            status = None
                elif stream_mode == "custom" and isinstance(chunk, dict):
                    content = None
                    status = chunk.get("status", "Processing")

                data = {
                    "message": content,
                    "status": status,
                    "session_id": session_id,
                    "org_id": org_id,
                    "custom_agent_name": agent_name,
                }
                yield f"data: {json.dumps(data)}\n\n"
            logger.info(f"Custom agent full message: {full_message}")

        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Error in custom agent chat: {str(e)}")
        return {
            "message": f"Error: {str(e)}",
            "session_id": session_id,
            "org_id": org_id,
        }


@app.post("/task-agent")
async def ask_task_agent(session_state: TaskSession = Depends(get_task_session_state)):
    """Task Agent API created based on the given task name."""

    task_agent = session_state.task_agent_graph
    response = task_agent.invoke({}, {"run_name": session_state.task.task_name})

    return {"message": "success", "response": response}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
