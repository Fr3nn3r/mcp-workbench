"""Mock MCP server implementation for testing.

This module provides a FastAPI-based mock server that implements the MCP specification
for testing purposes. It returns well-formed responses that match the schema.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import Dict, Any, Optional
import uvicorn
import logging

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

# Mock capabilities data
MOCK_CAPABILITIES = {"prompts": {"listChanged": True}}

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


def create_jsonrpc_response(id: Any, result: Any) -> Dict[str, Any]:
    """Create a JSON-RPC 2.0 response object."""
    return {"jsonrpc": "2.0", "id": id, "result": result}


def create_jsonrpc_error(id: Any, code: int, message: str) -> Dict[str, Any]:
    """Create a JSON-RPC 2.0 error response."""
    return {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}


@app.post("/")
async def handle_jsonrpc(request: Request) -> JSONResponse:
    """Handle JSON-RPC requests."""
    try:
        data = await request.json()
        logger.debug(f"Received request: {data}")
    except json.JSONDecodeError:
        return JSONResponse(
            create_jsonrpc_error(None, -32700, "Parse error"),
            status_code=200,  # Always return 200 for JSON-RPC
        )

    # Validate JSON-RPC request
    if not isinstance(data, dict):
        return JSONResponse(
            create_jsonrpc_error(None, -32600, "Invalid Request"), status_code=200
        )

    method = data.get("method")
    params = data.get("params", {})
    id = data.get("id")

    if not method or not isinstance(method, str):
        return JSONResponse(
            create_jsonrpc_error(id, -32600, "Invalid Request"), status_code=200
        )

    # Handle capabilities/get method
    if method == "capabilities/get":
        return JSONResponse(create_jsonrpc_response(id, MOCK_CAPABILITIES))

    # Handle prompts/list method
    elif method == "prompts/list":
        cursor = params.get("cursor") if params else None

        if cursor == "page2":
            return JSONResponse(create_jsonrpc_response(id, MOCK_PROMPTS_PAGE_2))
        elif cursor and cursor != "page2":
            return JSONResponse(
                create_jsonrpc_error(id, -32602, "Invalid cursor"), status_code=200
            )

        # Decide whether to use pagination based on params
        use_pagination = params.get("use_pagination", False)
        if use_pagination:
            return JSONResponse(create_jsonrpc_response(id, MOCK_PROMPTS_PAGE_1))
        else:
            return JSONResponse(create_jsonrpc_response(id, MOCK_PROMPTS))

    # Handle prompts/get method
    elif method == "prompts/get":
        name = params.get("name")
        arguments = params.get("arguments", {})

        # Validate prompt name
        if not name or name not in MOCK_PROMPT_CONTENT:
            return JSONResponse(
                create_jsonrpc_error(id, -32602, "Invalid prompt name"), status_code=200
            )

        # Get prompt definition
        prompt_def = next(
            (p for p in MOCK_PROMPTS["prompts"] if p["name"] == name), None
        )
        if not prompt_def:
            return JSONResponse(
                create_jsonrpc_error(id, -32603, "Internal error: prompt not found"),
                status_code=200,
            )

        # Validate required arguments
        for arg in prompt_def.get("arguments", []):
            if arg["required"] and arg["name"] not in arguments:
                return JSONResponse(
                    create_jsonrpc_error(
                        id, -32602, f"Missing required argument: {arg['name']}"
                    ),
                    status_code=200,
                )

            # Validate argument type
            if arg["name"] in arguments and not isinstance(arguments[arg["name"]], str):
                return JSONResponse(
                    create_jsonrpc_error(
                        id,
                        -32602,
                        f"Invalid type for argument {arg['name']}: expected string",
                    ),
                    status_code=200,
                )

        # Return mock content
        return JSONResponse(create_jsonrpc_response(id, MOCK_PROMPT_CONTENT[name]))

    # Method not found
    return JSONResponse(
        create_jsonrpc_error(id, -32601, f"Method {method} not found"), status_code=200
    )


def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Run the mock server."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
