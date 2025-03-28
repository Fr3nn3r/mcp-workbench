"""Mock MCP server implementation for testing.

This module provides a FastAPI-based mock server that implements the MCP specification
for testing purposes. It returns well-formed responses that match the schema.
"""

from fastapi import FastAPI, Request, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import Dict, Any, Optional, Union, List
import uvicorn
import logging
from pydantic import ValidationError

from mcp.protocol.schema import (
    JsonRpcRequest,
    JsonRpcResponse,
    ToolsListResult,
    PromptsListResult,
    PromptsGetResult,
    ResourcesListResult,
    ResourcesReadResult,
    ResourcesTemplatesListResult,
    ToolCallResult,
    CompletionResult,
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Mock MCP Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections
active_connections: List[WebSocket] = []

# Mock capabilities data
MOCK_CAPABILITIES = {
    "prompts": {"listChanged": True},
    "tools": {"listChanged": True},
    "resources": {"listChanged": True, "subscribe": True},
}

# Mock data for prompts
MOCK_PROMPTS = {
    "prompts": [
        {
            "name": "chat",
            "description": "A chat-style prompt that maintains conversation context",
            "arguments": [
                {
                    "name": "messages",
                    "description": "Array of message objects with role and content",
                    "required": True,
                },
                {
                    "name": "temperature",
                    "description": "Controls randomness in the response",
                    "required": False,
                },
            ],
        },
        {
            "name": "complete",
            "description": "Simple completion prompt",
            "arguments": [
                {
                    "name": "prompt",
                    "description": "The text prompt to complete",
                    "required": True,
                }
            ],
        },
    ]
}

# Mock data for prompts/get responses
MOCK_PROMPT_CONTENT = {
    "chat": {
        "description": "A chat conversation about Python programming",
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": "How do I write a Python function?",
                },
            },
            {
                "role": "assistant",
                "content": {
                    "type": "text",
                    "text": "To write a Python function, use the 'def' keyword followed by the function name and parameters in parentheses.",
                },
            },
            {
                "role": "assistant",
                "content": {
                    "type": "image",
                    "data": "base64_encoded_image_data",
                    "mimeType": "image/png",
                },
            },
            {
                "role": "assistant",
                "content": {
                    "type": "resource",
                    "resource": {
                        "uri": "https://docs.python.org/3/tutorial/controlflow.html#defining-functions",
                        "mimeType": "text/html",
                        "text": "Python documentation on defining functions",
                    },
                },
            },
        ],
    },
    "complete": {
        "description": "A simple completion example",
        "messages": [
            {
                "role": "user",
                "content": {"type": "text", "text": "Complete this code snippet"},
            },
            {
                "role": "assistant",
                "content": {"type": "text", "text": "Here's the completed code"},
            },
        ],
    },
}

# Mock data for pagination testing
MOCK_PROMPTS_PAGE_1 = {"prompts": [MOCK_PROMPTS["prompts"][0]], "nextCursor": "page2"}
MOCK_PROMPTS_PAGE_2 = {"prompts": [MOCK_PROMPTS["prompts"][1]]}

# Mock data for resources
MOCK_RESOURCES = [
    {
        "uri": "file://sample.txt",
        "name": "Sample Text",
        "description": "A sample text file",
        "mimeType": "text/plain",
    },
    {
        "uri": "file://image.png",
        "name": "Sample Image",
        "description": "A sample image file",
        "mimeType": "image/png",
    },
    {
        "uri": "file://doc.pdf",
        "name": "Sample PDF",
        "description": "A sample PDF file",
        "mimeType": "application/pdf",
    },
    {
        "uri": "file://data.json",
        "name": "Sample JSON",
        "description": "A sample JSON file",
        "mimeType": "application/json",
    },
]

# Split resources for pagination
MOCK_RESOURCES_PAGE_1 = {"resources": MOCK_RESOURCES[:2], "nextCursor": "page2"}
MOCK_RESOURCES_PAGE_2 = {"resources": MOCK_RESOURCES[2:], "nextCursor": None}

MOCK_RESOURCE_CONTENTS = {
    "file://sample.txt": {
        "type": "resource_text",
        "uri": "file://sample.txt",
        "mimeType": "text/plain",
        "text": "Hello, World!",
    },
    "file://image.png": {
        "type": "resource_blob",
        "uri": "file://image.png",
        "mimeType": "image/png",
        "blob": "base64encodeddata",
    },
}

MOCK_RESOURCE_TEMPLATES = [
    {
        "uriTemplate": "file://{name}.txt",
        "name": "Text File",
        "description": "Create a text file",
        "mimeType": "text/plain",
    },
    {
        "uriTemplate": "file://{name}.png",
        "name": "Image File",
        "description": "Create an image file",
        "mimeType": "image/png",
    },
]

# Mock data for tools
MOCK_TOOLS = [
    {
        "name": "get_weather",
        "description": "Get current weather information for a location",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name or zip code"}
            },
            "required": ["location"],
        },
    },
    {
        "name": "search_web",
        "description": "Search the web for information",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    },
]

# Split tools for pagination
MOCK_TOOLS_PAGE_1 = {"tools": [MOCK_TOOLS[0]], "nextCursor": "page2"}
MOCK_TOOLS_PAGE_2 = {"tools": [MOCK_TOOLS[1]], "nextCursor": None}

# Mock data for completion
MOCK_COMPLETIONS = {
    "prompt": {"chat": {"messages": ["Hi", "Hello", "How are you?"]}},
    "resource": {"file://{name}.txt": ["example", "test", "sample"]},
}


def create_jsonrpc_response(
    id: Optional[Union[int, str]], result: Any
) -> Dict[str, Any]:
    """Create a JSON-RPC response object."""
    return JsonRpcResponse(jsonrpc="2.0", id=id, result=result).dict()


def create_jsonrpc_error(
    id: Optional[Union[int, str]], code: int, message: str
) -> Dict[str, Any]:
    """Create a JSON-RPC error response object."""
    return JsonRpcResponse(
        jsonrpc="2.0", id=id, error={"code": code, "message": message}
    ).dict()


def create_jsonrpc_notification(method: str, params: Any) -> Dict[str, Any]:
    """Create a JSON-RPC notification object."""
    return JsonRpcResponse(jsonrpc="2.0", method=method, params=params).dict()


@app.post("/")
async def handle_jsonrpc(request: Request) -> JSONResponse:
    """Handle JSON-RPC requests."""
    try:
        # Parse request body
        body = await request.json()

        # Validate request against schema
        try:
            rpc_request = JsonRpcRequest(**body)
        except ValidationError as e:
            return JSONResponse(
                content=create_jsonrpc_error(
                    body.get("id"), -32600, f"Invalid Request: {str(e)}"
                ),
                media_type="application/json",
            )

        method = rpc_request.method
        params = rpc_request.params or {}
        id = rpc_request.id

        # Handle capabilities/get method
        if method == "capabilities/get":
            return JSONResponse(
                content=create_jsonrpc_response(id, MOCK_CAPABILITIES),
                media_type="application/json",
            )

        # Handle tools/list method
        elif method == "tools/list":
            cursor = params.get("cursor")
            use_pagination = params.get("use_pagination")

            # Validate parameters
            if cursor is not None and not isinstance(cursor, str):
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32602, "Invalid cursor type"),
                    media_type="application/json",
                )
            if use_pagination is not None and not isinstance(use_pagination, bool):
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32602, "Invalid pagination type"),
                    media_type="application/json",
                )

            # Handle pagination
            if cursor == "page2":
                result = ToolsListResult(tools=MOCK_TOOLS[2:], nextCursor=None)
            elif cursor and cursor != "page2":
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32602, "Invalid cursor value"),
                    media_type="application/json",
                )
            elif use_pagination or cursor:
                result = ToolsListResult(tools=MOCK_TOOLS[:2], nextCursor="page2")
            else:
                result = ToolsListResult(tools=MOCK_TOOLS, nextCursor=None)

            return JSONResponse(
                content=create_jsonrpc_response(id, result.dict()),
                media_type="application/json",
            )

        # Handle tools/call method
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            if not tool_name or not isinstance(tool_name, str):
                return JSONResponse(
                    content=create_jsonrpc_error(
                        id, -32602, "Missing or invalid tool name"
                    ),
                    media_type="application/json",
                )

            # Find the tool
            tool = next((t for t in MOCK_TOOLS if t["name"] == tool_name), None)
            if not tool:
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32602, "Tool not found"),
                    media_type="application/json",
                )

            # Mock successful tool call
            result = ToolCallResult(
                content=[
                    {
                        "type": "text",
                        "text": f"Mock result for {tool_name} with args: {tool_args}",
                    }
                ],
                isError=False,
            )

            return JSONResponse(
                content=create_jsonrpc_response(id, result.dict()),
                media_type="application/json",
            )

        # Handle completion/complete method
        elif method == "completion/complete":
            ref = params.get("ref")
            if not ref or not isinstance(ref, dict):
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32602, "Invalid ref parameter"),
                    media_type="application/json",
                )

            ref_type = ref.get("type")
            if ref_type == "ref/prompt":
                prompt_name = ref.get("name")
                arg = params.get("argument", {})
                arg_name = arg.get("name")
                arg_value = arg.get("value", "")

                if not prompt_name or not arg_name:
                    return JSONResponse(
                        content=create_jsonrpc_error(
                            id, -32602, "Missing required parameters"
                        ),
                        media_type="application/json",
                    )

                # Get completions for prompt argument
                completions = (
                    MOCK_COMPLETIONS["prompt"].get(prompt_name, {}).get(arg_name, [])
                )
                filtered = [v for v in completions if arg_value.lower() in v.lower()]
                result = {
                    "completion": {
                        "values": filtered[:10],
                        "hasMore": len(filtered) > 10,
                        "total": len(filtered),
                    }
                }

            elif ref_type == "ref/resource":
                uri = ref.get("uri")
                value = params.get("value", "")

                if not uri:
                    return JSONResponse(
                        content=create_jsonrpc_error(
                            id, -32602, "Missing URI parameter"
                        ),
                        media_type="application/json",
                    )

                # Get completions for resource URI
                completions = MOCK_COMPLETIONS["resource"].get(uri, [])
                filtered = [v for v in completions if value.lower() in v.lower()]
                result = {
                    "completion": {
                        "values": filtered[:10],
                        "hasMore": len(filtered) > 10,
                        "total": len(filtered),
                    }
                }

            else:
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32602, "Invalid ref type"),
                    media_type="application/json",
                )

            return JSONResponse(
                content=create_jsonrpc_response(id, result),
                media_type="application/json",
            )

        # Handle prompts/list method
        elif method == "prompts/list":
            cursor = params.get("cursor")
            use_pagination = params.get("use_pagination")

            # Validate parameters
            if cursor is not None and not isinstance(cursor, str):
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32602, "Invalid cursor type"),
                    media_type="application/json",
                )
            if use_pagination is not None and not isinstance(use_pagination, bool):
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32602, "Invalid pagination type"),
                    media_type="application/json",
                )

            # Handle pagination
            if cursor == "page2":
                result = PromptsListResult(**MOCK_PROMPTS_PAGE_2)
            elif cursor and cursor != "page2":
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32602, "Invalid cursor value"),
                    media_type="application/json",
                )
            elif use_pagination or cursor:
                result = PromptsListResult(**MOCK_PROMPTS_PAGE_1)
            else:
                result = PromptsListResult(**MOCK_PROMPTS)

            return JSONResponse(
                content=create_jsonrpc_response(id, result.dict()),
                media_type="application/json",
            )

        # Handle prompts/get method
        elif method == "prompts/get":
            name = params.get("name")
            if not name:
                return JSONResponse(
                    content=create_jsonrpc_error(
                        id, -32602, "Missing required parameter: name"
                    ),
                    media_type="application/json",
                )
            if not isinstance(name, str):
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32602, "Invalid name type"),
                    media_type="application/json",
                )

            content = MOCK_PROMPT_CONTENT.get(name)
            if not content:
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32602, "Prompt not found"),
                    media_type="application/json",
                )

            result = PromptsGetResult(**content)
            return JSONResponse(
                content=create_jsonrpc_response(id, result.dict()),
                media_type="application/json",
            )

        # Resources endpoints
        elif method == "resources/list":
            cursor = params.get("cursor")
            use_pagination = params.get("use_pagination")

            # Validate parameters
            if cursor is not None and not isinstance(cursor, str):
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32602, "Invalid cursor type"),
                    media_type="application/json",
                )
            if use_pagination is not None and not isinstance(use_pagination, bool):
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32602, "Invalid pagination type"),
                    media_type="application/json",
                )

            # Handle pagination
            if cursor == "page2":
                result = ResourcesListResult(**MOCK_RESOURCES_PAGE_2)
            elif cursor and cursor != "page2":
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32602, "Invalid cursor value"),
                    media_type="application/json",
                )
            elif use_pagination or cursor:
                result = ResourcesListResult(**MOCK_RESOURCES_PAGE_1)
            else:
                result = ResourcesListResult(resources=MOCK_RESOURCES, nextCursor=None)

            return JSONResponse(
                content=create_jsonrpc_response(id, result.dict()),
                media_type="application/json",
            )

        elif method == "resources/read":
            uri = params.get("uri")
            if not uri:
                return JSONResponse(
                    content=create_jsonrpc_error(
                        id, -32602, "Missing required parameter: uri"
                    ),
                    media_type="application/json",
                )
            if not isinstance(uri, str):
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32602, "Invalid uri type"),
                    media_type="application/json",
                )

            content = MOCK_RESOURCE_CONTENTS.get(uri)
            if not content:
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32002, "Resource not found"),
                    media_type="application/json",
                )

            result = ResourcesReadResult(contents=[content])
            return JSONResponse(
                content=create_jsonrpc_response(id, result.dict()),
                media_type="application/json",
            )

        elif method == "resources/templates/list":
            result = ResourcesTemplatesListResult(
                resourceTemplates=MOCK_RESOURCE_TEMPLATES
            )
            return JSONResponse(
                content=create_jsonrpc_response(id, result.dict()),
                media_type="application/json",
            )

        elif method == "resources/subscribe":
            uri = params.get("uri")
            if not uri:
                return JSONResponse(
                    content=create_jsonrpc_error(
                        id, -32602, "Missing required parameter: uri"
                    ),
                    media_type="application/json",
                )
            if not isinstance(uri, str):
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32602, "Invalid uri type"),
                    media_type="application/json",
                )

            if uri not in MOCK_RESOURCE_CONTENTS:
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32002, "Resource not found"),
                    media_type="application/json",
                )

            return JSONResponse(
                content=create_jsonrpc_response(
                    id, {"subscriptionId": "mock_subscription_1"}
                ),
                media_type="application/json",
            )

        elif method == "resources/unsubscribe":
            subscription_id = params.get("subscriptionId")
            if not subscription_id:
                return JSONResponse(
                    content=create_jsonrpc_error(
                        id, -32602, "Missing required parameter: subscriptionId"
                    ),
                    media_type="application/json",
                )
            if not isinstance(subscription_id, str):
                return JSONResponse(
                    content=create_jsonrpc_error(
                        id, -32602, "Invalid subscriptionId type"
                    ),
                    media_type="application/json",
                )

            if subscription_id != "mock_subscription_1":
                return JSONResponse(
                    content=create_jsonrpc_error(id, -32602, "Invalid subscription ID"),
                    media_type="application/json",
                )

            return JSONResponse(
                content=create_jsonrpc_response(id, {}),
                media_type="application/json",
            )

        # Method not found
        return JSONResponse(
            content=create_jsonrpc_error(id, -32601, f"Method {method} not found"),
            media_type="application/json",
        )

    except Exception as e:
        return JSONResponse(
            content=create_jsonrpc_error(None, -32603, str(e)),
            media_type="application/json",
        )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for notifications."""
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except Exception:
        active_connections.remove(websocket)


async def broadcast_tools_changed():
    """Broadcast tools/list_changed notification to all connected clients."""
    notification = create_jsonrpc_notification(
        "tools/list_changed", {"message": "Tools list has been updated"}
    )
    for connection in active_connections:
        try:
            await connection.send_json(notification)
        except Exception:
            active_connections.remove(connection)


def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Run the mock server."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
