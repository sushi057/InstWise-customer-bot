import json
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

from fastapi.responses import StreamingResponse
from langchain_core.runnables import RunnableConfig


async def create_event_stream(
    graph,
    query: str,
    config: RunnableConfig,
    stream_modes: List[str],
    data_formatter: Callable[[Optional[str], Optional[str], Dict[str, Any]], Dict[str, Any]],
    additional_input: Dict[str, Any] | None = None,
) -> AsyncGenerator[str, None]:
    """
    Create an event stream for SSE responses.
    
    Args:
        graph: The langgraph graph to stream from
        query: The user's query string
        config: The runnable configuration
        stream_modes: The stream modes to use (e.g., ["messages", "custom"])
        data_formatter: A function that formats the data to be sent in the stream
                        It receives (content, status, extra_data) and returns a dict
        additional_input: Additional data to include in the input dictionary
    
    Yields:
        Formatted SSE data strings
    """
    # Build input data with the query
    input_data = {"messages": [("user", query)]}
    
    # Add any additional input parameters
    if additional_input:
        input_data.update(additional_input)
    
    async for stream_mode, chunk in graph.astream(
        input_data,
        config,
        stream_mode=stream_modes,
    ):
        content = None
        status = "Processing"
        
        if stream_mode == "messages":
            message, metadata = chunk
            node_name = metadata.get("langgraph_node", "")
            
            if "tools" not in node_name:
                if hasattr(message, "tool_calls") and message.tool_calls:
                    content = None
                    status = "Analyzing query"
                elif hasattr(message, "content") and message.content != "":
                    content = message.content
                    status = None
            elif node_name == "fetch_user_info":
                content = message.content
                status = None
        elif stream_mode == "custom" and isinstance(chunk, dict):
            content = None
            status = chunk.get("status", "Processing")
        
        data = data_formatter(content, status, {"stream_mode": stream_mode, "chunk": chunk})
        yield f"data: {json.dumps(data)}\n\n"


def create_streaming_response(
    graph,
    query: str,
    config: RunnableConfig,
    stream_modes: List[str],
    data_formatter: Callable[[Optional[str], Optional[str], Dict[str, Any]], Dict[str, Any]],
    additional_input: Dict[str, Any] | None = None,
) -> StreamingResponse:
    """
    Create a StreamingResponse for SSE.
    
    Args:
        graph: The langgraph graph to stream from
        query: The user's query string
        config: The runnable configuration
        stream_modes: The stream modes to use (e.g., ["messages", "custom"])
        data_formatter: A function that formats the data to be sent in the stream
        additional_input: Additional data to include in the input dictionary
    
    Returns:
        A FastAPI StreamingResponse
    """
    return StreamingResponse(
        create_event_stream(graph, query, config, stream_modes, data_formatter, additional_input),
        media_type="text/event-stream"
    )
