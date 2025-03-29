import json
import time
from flask import Flask, request, jsonify, Response

app = Flask(__name__)


# Store server state
class ServerState:
    def __init__(self):
        # Response definitions (same as MockMCPClient in conftest.py)
        self.responses = {
            "prompts/list": {
                "prompts": [
                    {
                        "name": "test_prompt",
                        "description": "A test prompt",
                        "arguments": [
                            {
                                "name": "arg1",
                                "description": "Test argument",
                                "required": True,
                            }
                        ],
                    },
                    {
                        "name": "simple_prompt",
                        "description": "A prompt with no arguments",
                    },
                    {
                        "name": "echo_prompt",
                        "description": "Repeats user input",
                        "arguments": [
                            {
                                "name": "text",
                                "description": "input text",
                                "required": True,
                            }
                        ],
                    },
                ]
            },
            # Resources endpoints
            "resources/list": {
                "resources": [
                    {
                        "uri": "example://resource1",
                        "name": "Example Resource 1",
                        "mimeType": "text/plain",
                    },
                    {
                        "uri": "example://resource2",
                        "name": "Example Resource 2",
                        "mimeType": "application/json",
                    },
                ]
            },
            "resources/templates/list": {
                "resourceTemplates": [
                    {
                        "uriTemplate": "template://example/{name}",
                        "name": "Example Template",
                        "mimeType": "text/plain",
                    },
                    {
                        "uriTemplate": "template://config/{filename}",
                        "name": "Configuration Template",
                        "mimeType": "application/json",
                    },
                ]
            },
            # Tools endpoints
            "tools/list": {
                "tools": [
                    {
                        "name": "example_tool",
                        "description": "An example tool for testing",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "A search query",
                                }
                            },
                            "required": ["query"],
                        },
                    },
                    {
                        "name": "calculator",
                        "description": "Performs basic calculations",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "expression": {
                                    "type": "string",
                                    "description": "Math expression to evaluate",
                                }
                            },
                            "required": ["expression"],
                        },
                    },
                    {
                        "name": "error_tool",
                        "description": "A tool that produces controlled errors",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "mode": {
                                    "type": "string",
                                    "description": "Error mode to trigger",
                                }
                            },
                            "required": ["mode"],
                        },
                    },
                    {
                        "name": "admin_only_tool",
                        "description": "A tool that requires admin privileges",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "Admin command to execute",
                                }
                            },
                            "required": ["command"],
                        },
                    },
                    {
                        "name": "echo_tool",
                        "description": "A tool that echoes back user input",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {
                                    "type": "string",
                                    "description": "Text to echo back",
                                }
                            },
                            "required": ["text"],
                        },
                    },
                    {
                        "name": "echo",
                        "description": "A tool that echoes the input text",
                        "inputSchema": {
                            "type": "object",
                            "required": ["text"],
                            "properties": {
                                "text": {
                                    "type": "string",
                                    "description": "Text to echo back",
                                }
                            },
                        },
                    },
                ]
            },
        }
        self.capabilities = {
            "prompts": {"list": True, "get": True, "listChanged": True},
            "resources": {
                "list": True,
                "read": True,
                "templates": {"list": True},
                "listChanged": True,
                "subscribe": True,
            },
            "tools": {"list": True, "call": True, "listChanged": True},
            "completion": {"complete": True},
        }
        self.call_count = {}
        self.call_reset_time = time.time()
        # Configuration for simulating errors or special cases
        self.simulate_errors = False
        self.slow_response = False
        self.force_invalid_json = False


# Create server state
state = ServerState()


def create_error_response(id, code, message, data=None):
    """Create a JSON-RPC error response"""
    response = {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}
    if data:
        response["error"]["data"] = data
    return response


def create_success_response(id, result):
    """Create a JSON-RPC success response"""
    return {"jsonrpc": "2.0", "id": id, "result": result}


def validate_jsonrpc_request(req):
    """Validate basic JSON-RPC request format"""
    # Check for required fields
    if "jsonrpc" not in req:
        return create_error_response(
            req.get("id", None), -32600, "Invalid Request: jsonrpc field is required"
        )

    if req["jsonrpc"] != "2.0":
        return create_error_response(
            req.get("id", None),
            -32600,
            "Invalid Request: jsonrpc version must be exactly '2.0'",
        )

    if "method" not in req:
        return create_error_response(
            req.get("id", None), -32600, "Invalid Request: method is required"
        )

    if not isinstance(req["method"], str):
        return create_error_response(
            req.get("id", None), -32600, "Invalid Request: method must be a string"
        )

    return None


def handle_prompts_get(req_id, params):
    """Handle prompts/get requests"""
    name = params.get("name")
    arguments = params.get("arguments", {})

    # Simulate an internal server error for testing
    if name == "cause_internal_error":
        return create_error_response(
            req_id, -32603, "Internal error: prompt processor failed"
        )

    # Find the prompt in our list
    prompts_list = state.responses["prompts/list"]["prompts"]
    prompt = next((p for p in prompts_list if p["name"] == name), None)

    # Invalid prompt name error
    if not prompt:
        return create_error_response(
            req_id, -32602, "Invalid params: unknown prompt name"
        )

    # Check required arguments
    if "arguments" in prompt:
        for arg in prompt["arguments"]:
            if arg["required"] and arg["name"] not in arguments:
                return create_error_response(
                    req_id, -32602, "Invalid params: missing required argument"
                )

    # Create successful response
    if name == "echo_prompt":
        text = arguments.get("text", "")
        result = {
            "description": "Echo prompt result",
            "messages": [
                {
                    "role": "user",
                    "content": {"type": "text", "text": f"You said: {text}"},
                }
            ],
        }
        return create_success_response(req_id, result)

    if name == "test_prompt":
        result = {
            "description": prompt["description"],
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"User message with argument: {arguments.get('arg1', '')}",
                    },
                },
                {
                    "role": "assistant",
                    "content": {"type": "text", "text": "Assistant response"},
                },
            ],
        }
        return create_success_response(req_id, result)
    else:
        # Generic response for other prompts
        result = {
            "description": prompt.get("description"),
            "messages": [
                {
                    "role": "user",
                    "content": {"type": "text", "text": "Default user message"},
                },
                {
                    "role": "assistant",
                    "content": {
                        "type": "resource",
                        "resource": {
                            "uri": "example://resource",
                            "mimeType": "text/plain",
                            "text": "Example resource content",
                        },
                    },
                },
            ],
        }
        return create_success_response(req_id, result)


def handle_resources_read(req_id, params):
    """Handle resources/read requests"""
    uri = params.get("uri")
    if not uri:
        return create_error_response(
            req_id, -32602, "Invalid params: missing uri parameter"
        )

    # Check if the URI is nonexistent.fake which is our test case
    if "nonexistent" in uri:
        return create_error_response(req_id, -32002, "Resource not found")

    # Find the resource in our list
    resources_list = state.responses["resources/list"]["resources"]
    resource = next((r for r in resources_list if r["uri"] == uri), None)

    if not resource:
        return create_error_response(
            req_id, -32602, "Invalid params: unknown resource uri"
        )

    # Return the resource content
    result = {
        "contents": [
            {
                "uri": uri,
                "mimeType": resource["mimeType"],
                "text": f"Content of {resource['name']}",
            }
        ]
    }
    return create_success_response(req_id, result)


def handle_resources_subscribe(req_id, params):
    """Handle resources/subscribe requests"""
    uri = params.get("uri")
    if not uri:
        return create_error_response(
            req_id, -32602, "Invalid params: missing uri parameter"
        )

    # Find the resource in our list
    resources_list = state.responses["resources/list"]["resources"]
    resource = next((r for r in resources_list if r["uri"] == uri), None)

    if not resource:
        return create_error_response(
            req_id, -32602, "Invalid params: unknown resource uri"
        )

    # Return a success response
    result = {"status": "subscribed", "uri": uri}
    return create_success_response(req_id, result)


def handle_tools_call(req_id, params):
    """Handle tools/call requests"""
    name = params.get("name")
    arguments = params.get("arguments", {})

    # Find tool in list
    tools_list = state.responses["tools/list"]["tools"]
    tool = next((t for t in tools_list if t["name"] == name), None)

    if not tool:
        return create_error_response(
            req_id, -32602, "Invalid params: unknown tool name"
        )

    # Check required arguments
    schema = tool.get("inputSchema", {})
    for required_arg in schema.get("required", []):
        if required_arg not in arguments:
            return create_error_response(
                req_id,
                -32602,
                f"Invalid params: missing required argument {required_arg}",
            )

    # Handle access control for admin_only_tool
    if name == "admin_only_tool":
        return create_error_response(
            req_id, -32602, "Unauthorized: admin privileges required"
        )

    # Handle rate limiting
    current_time = time.time()
    # Reset counts if more than 60 seconds have passed
    if current_time - state.call_reset_time > 60:
        state.call_count = {}
        state.call_reset_time = current_time

    # Increment call count for this tool
    state.call_count[name] = state.call_count.get(name, 0) + 1

    # Check rate limit (10 calls per minute)
    if state.call_count[name] > 10:
        return create_error_response(req_id, -32005, "Rate limit exceeded")

    # Handle error_tool specifically
    if name == "error_tool":
        mode = arguments.get("mode", "")
        if mode.lower() in ["trigger", "error", "fail", "failure", "trigger error"]:
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": "Error occurred: The external API returned a rate limit exceeded error.",
                    }
                ],
                "isError": True,
            }
            return create_success_response(req_id, result)

    # Handle echo_tool specifically
    if name == "echo_tool":
        text = arguments.get("text", "")
        # Basic sanitization for demonstration purposes
        sanitized_text = text.replace("<script>", "").replace("</script>", "")
        result = {
            "content": [
                {
                    "type": "text",
                    "text": f"Echo: {sanitized_text}",
                }
            ]
        }
        return create_success_response(req_id, result)

    # Handle the echo tool specifically (with different response format)
    if name == "echo":
        text = arguments.get("text", "")
        # Basic sanitization for demonstration purposes
        sanitized_text = text.replace("<script>", "&lt;script&gt;").replace(
            "</script>", "&lt;/script&gt;"
        )
        # Remove dangerous HTML attributes
        sanitized_text = sanitized_text.replace("onerror=", "data-removed=")
        sanitized_text = sanitized_text.replace("onclick=", "data-removed=")
        result = {"output": sanitized_text}
        return create_success_response(req_id, result)

    # Return tool execution result
    result = {
        "content": [
            {
                "type": "text",
                "text": f"Tool {name} executed successfully with arguments: {arguments}",
            }
        ]
    }
    return create_success_response(req_id, result)


def handle_completion_complete(req_id, params):
    """Handle completion/complete requests"""
    ref = params.get("ref", {})
    argument = params.get("argument", {})

    ref_type = ref.get("type")

    if ref_type == "ref/prompt":
        # Handle prompt argument completion
        prompt_name = ref.get("name")
        arg_name = argument.get("name")
        arg_value = argument.get("value", "")

        # Validate prompt exists
        prompts_list = state.responses["prompts/list"]["prompts"]
        prompt = next((p for p in prompts_list if p["name"] == prompt_name), None)
        if not prompt:
            return create_error_response(
                req_id, -32602, f"Invalid params: unknown prompt name '{prompt_name}'"
            )

        # Validate argument exists if the prompt has arguments
        if "arguments" in prompt:
            arg = next((a for a in prompt["arguments"] if a["name"] == arg_name), None)
            if not arg:
                return create_error_response(
                    req_id,
                    -32602,
                    f"Invalid params: unknown argument '{arg_name}' for prompt '{prompt_name}'",
                )

        # Return completions based on the input
        result = {
            "completion": {
                "values": [
                    f"{arg_value}ample",
                    f"{arg_value}pert",
                    f"{arg_value}cellent",
                ],
                "hasMore": False,
            }
        }
        return create_success_response(req_id, result)
    elif ref_type == "ref/resource":
        # Handle resource URI completion
        uri = ref.get("uri")
        arg_name = argument.get("name")
        arg_value = argument.get("value", "")

        # Return completions based on the input
        result = {
            "completion": {
                "values": [
                    f"{arg_value}file1.txt",
                    f"{arg_value}file2.json",
                    f"{arg_value}directory/",
                ],
                "hasMore": False,
            }
        }
        return create_success_response(req_id, result)
    else:
        return create_error_response(
            req_id, -32602, f"Invalid params: unsupported ref type {ref_type}"
        )


@app.route("/", methods=["POST"])
def handle_rpc():
    """Main JSON-RPC handler"""
    # Test for invalid JSON
    if state.force_invalid_json:
        # Reset the flag for next request
        state.force_invalid_json = False
        return Response("Not a valid JSON", status=400, mimetype="text/plain")

    try:
        req = request.get_json()
    except Exception:
        return Response("Invalid JSON", status=400, mimetype="text/plain")

    # Extract basic fields
    req_id = req.get("id", 1)

    # Validate JSON-RPC request format
    error = validate_jsonrpc_request(req)
    if error:
        return jsonify(error)

    # Get method and params
    method = req.get("method")
    params = req.get("params", {})

    # Simulate slow response if configured
    if state.slow_response:
        time.sleep(2)

    # Server capabilities
    if method == "server/capabilities":
        return jsonify(
            create_success_response(req_id, {"capabilities": state.capabilities})
        )

    # Prompts endpoints
    elif method == "prompts/list":
        return jsonify(create_success_response(req_id, state.responses["prompts/list"]))

    elif method == "prompts/get":
        return jsonify(handle_prompts_get(req_id, params))

    # Resources endpoints
    elif method == "resources/list":
        return jsonify(
            create_success_response(req_id, state.responses["resources/list"])
        )

    elif method == "resources/templates/list":
        return jsonify(
            create_success_response(req_id, state.responses["resources/templates/list"])
        )

    elif method == "resources/read":
        return jsonify(handle_resources_read(req_id, params))

    elif method == "resources/subscribe":
        return jsonify(handle_resources_subscribe(req_id, params))

    # Tools endpoints
    elif method == "tools/list":
        return jsonify(create_success_response(req_id, state.responses["tools/list"]))

    elif method == "tools/call":
        return jsonify(handle_tools_call(req_id, params))

    # Completion endpoints
    elif method == "completion/complete":
        return jsonify(handle_completion_complete(req_id, params))

    # Unknown method
    else:
        return jsonify(create_error_response(req_id, -32601, "Method not found"))


@app.route("/admin/config", methods=["POST"])
def configure_server():
    """Admin endpoint to configure server behavior"""
    config = request.get_json()

    if "simulate_errors" in config:
        state.simulate_errors = config["simulate_errors"]

    if "slow_response" in config:
        state.slow_response = config["slow_response"]

    if "force_invalid_json" in config:
        state.force_invalid_json = config["force_invalid_json"]

    return jsonify(
        {
            "status": "ok",
            "config": {
                "simulate_errors": state.simulate_errors,
                "slow_response": state.slow_response,
                "force_invalid_json": state.force_invalid_json,
            },
        }
    )


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    """Simple health check endpoint"""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
