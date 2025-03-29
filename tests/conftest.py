import pytest
from unittest.mock import MagicMock
import time
import httpx


class MockMCPClient:
    """A mock client for testing MCP protocol interactions."""

    def __init__(self):
        self.responses = {
            "prompts/list": {
                "result": {
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
                    ]
                }
            },
            # Resources endpoints
            "resources/list": {
                "result": {
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
                }
            },
            "resources/templates/list": {
                "result": {
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
                }
            },
            # Tools endpoints
            "tools/list": {
                "result": {
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
                }
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
        self.prompt_list_changes = False
        self.tool_list_changes = False
        self._change_timer = 0
        self._tool_change_timer = 0
        self._call_count = {}  # Track tool call counts for rate limiting
        self._call_reset_time = time.time()

        # Add session and base_url for raw JSON-RPC testing
        self.session = httpx.Client()
        self.base_url = "http://localhost:8000"  # Default mock URL

    def send(self, method, params=None):
        """Simulate sending a request to an MCP server."""
        if method == "prompts/get":
            return self._handle_prompts_get(params or {})

        if method == "resources/read":
            return self._handle_resources_read(params or {})

        if method == "resources/subscribe":
            return self._handle_resources_subscribe(params or {})

        if method == "tools/call":
            return self._handle_tools_call(params or {})

        if method == "completion/complete":
            return self._handle_completion_complete(params or {})

        # Handle prompts/list with possible changes
        if method == "prompts/list":
            if self.prompt_list_changes and time.time() - self._change_timer > 5:
                # Simulate list change after 5 seconds
                self.responses["prompts/list"]["result"]["prompts"].append(
                    {
                        "name": "dynamic_prompt",
                        "description": "A dynamically added prompt",
                    }
                )
                self.prompt_list_changes = False
            return self.responses["prompts/list"]

        # Handle tools/list with possible changes
        if method == "tools/list":
            if self.tool_list_changes and time.time() - self._tool_change_timer > 3:
                # Simulate list change after 3 seconds
                self.responses["tools/list"]["result"]["tools"].append(
                    {
                        "name": "dynamic_tool",
                        "description": "A dynamically added tool",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "dynamic_param": {
                                    "type": "string",
                                    "description": "A dynamic parameter",
                                }
                            },
                            "required": ["dynamic_param"],
                        },
                    }
                )
                self.tool_list_changes = False
            return self.responses["tools/list"]

        if method in self.responses:
            return self.responses[method]

        raise ValueError(f"Method {method} not supported in mock client")

    def get_capabilities(self):
        """Return the server capabilities."""
        return self.capabilities

    def simulate_prompt_change(self):
        """Prepare the client to simulate a change in the prompt list."""
        self.prompt_list_changes = True
        self._change_timer = time.time()

    def simulate_tool_change(self):
        """Prepare the client to simulate a change in the tool list."""
        self.tool_list_changes = True
        self._tool_change_timer = time.time()

    def _handle_prompts_get(self, params):
        """Handle prompts/get requests with validation."""
        name = params.get("name")
        arguments = params.get("arguments", {})

        # Simulate an internal server error for testing
        if name == "cause_internal_error":
            raise ValueError("Internal error: prompt processor failed (-32603)")

        # Find the prompt in our list
        prompts_list = self.responses["prompts/list"]["result"]["prompts"]
        prompt = next((p for p in prompts_list if p["name"] == name), None)

        # Invalid prompt name error
        if not prompt:
            raise ValueError("Invalid params: unknown prompt name (-32602)")

        # Check required arguments
        if "arguments" in prompt:
            for arg in prompt["arguments"]:
                if arg["required"] and arg["name"] not in arguments:
                    raise ValueError(
                        "Invalid params: missing required argument (-32602)"
                    )

        # Create successful response
        if name == "test_prompt":
            return {
                "result": {
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
            }
        else:
            # Generic response for other prompts
            return {
                "result": {
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
            }

    def _handle_resources_read(self, params):
        """Handle resources/read requests."""
        uri = params.get("uri")
        if not uri:
            raise ValueError("Invalid params: missing uri parameter (-32602)")

        # Check if the URI is nonexistent.fake which is our test case
        if "nonexistent" in uri:
            raise ValueError("Resource not found (-32002)")

        # Find the resource in our list
        resources_list = self.responses["resources/list"]["result"]["resources"]
        resource = next((r for r in resources_list if r["uri"] == uri), None)

        if not resource:
            raise ValueError("Invalid params: unknown resource uri (-32602)")

        # Return the resource content
        return {
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": resource["mimeType"],
                        "text": f"Content of {resource['name']}",
                    }
                ]
            }
        }

    def _handle_resources_subscribe(self, params):
        """Handle resources/subscribe requests."""
        uri = params.get("uri")
        if not uri:
            raise ValueError("Invalid params: missing uri parameter (-32602)")

        # Find the resource in our list
        resources_list = self.responses["resources/list"]["result"]["resources"]
        resource = next((r for r in resources_list if r["uri"] == uri), None)

        if not resource:
            raise ValueError("Invalid params: unknown resource uri (-32602)")

        # Return a success response
        return {"result": {"status": "subscribed", "uri": uri}}

    def _handle_tools_call(self, params):
        """Handle tools/call requests."""
        name = params.get("name")
        arguments = params.get("arguments", {})

        # Find tool in list
        tools_list = self.responses["tools/list"]["result"]["tools"]
        tool = next((t for t in tools_list if t["name"] == name), None)

        if not tool:
            raise ValueError("Invalid params: unknown tool name (-32602)")

        # Check required arguments
        schema = tool.get("inputSchema", {})
        for required_arg in schema.get("required", []):
            if required_arg not in arguments:
                raise ValueError(
                    f"Invalid params: missing required argument {required_arg} (-32602)"
                )

        # Handle access control for admin_only_tool
        if name == "admin_only_tool":
            raise ValueError("Unauthorized: admin privileges required (-32602)")

        # Handle rate limiting
        current_time = time.time()
        # Reset counts if more than 60 seconds have passed
        if current_time - self._call_reset_time > 60:
            self._call_count = {}
            self._call_reset_time = current_time

        # Increment call count for this tool
        self._call_count[name] = self._call_count.get(name, 0) + 1

        # Check rate limit (10 calls per minute)
        if self._call_count[name] > 10:
            raise ValueError("Rate limit exceeded (-32005)")

        # Handle error_tool specifically
        if name == "error_tool":
            mode = arguments.get("mode", "")
            if mode.lower() in ["trigger", "error", "fail", "failure", "trigger error"]:
                return {
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": "Error occurred: The external API returned a rate limit exceeded error.",
                            }
                        ],
                        "isError": True,
                    }
                }

        # Handle echo_tool specifically
        if name == "echo_tool":
            text = arguments.get("text", "")
            # Basic sanitization for demonstration purposes
            sanitized_text = text.replace("<script>", "").replace("</script>", "")
            return {
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Echo: {sanitized_text}",
                        }
                    ]
                }
            }

        # Handle the echo tool
        if name == "echo":
            text = arguments.get("text", "")
            # Basic sanitization for demonstration purposes
            sanitized_text = text.replace("<script>", "&lt;script&gt;").replace(
                "</script>", "&lt;/script&gt;"
            )
            # Remove dangerous HTML attributes
            sanitized_text = sanitized_text.replace("onerror=", "data-removed=")
            sanitized_text = sanitized_text.replace("onclick=", "data-removed=")
            return {"result": {"output": sanitized_text}}

        # Return tool execution result
        return {
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"Tool {name} executed successfully with arguments: {arguments}",
                    }
                ]
            }
        }

    def _handle_completion_complete(self, params):
        """Handle completion/complete requests."""
        ref = params.get("ref", {})
        argument = params.get("argument", {})

        ref_type = ref.get("type")

        if ref_type == "ref/prompt":
            # Handle prompt argument completion
            prompt_name = ref.get("name")
            arg_name = argument.get("name")
            arg_value = argument.get("value", "")

            # Validate prompt exists
            prompts_list = self.responses["prompts/list"]["result"]["prompts"]
            prompt = next((p for p in prompts_list if p["name"] == prompt_name), None)
            if not prompt:
                raise ValueError(
                    f"Invalid params: unknown prompt name '{prompt_name}' (-32602)"
                )

            # Validate argument exists if the prompt has arguments
            if "arguments" in prompt:
                arg = next(
                    (a for a in prompt["arguments"] if a["name"] == arg_name), None
                )
                if not arg:
                    raise ValueError(
                        f"Invalid params: unknown argument '{arg_name}' for prompt '{prompt_name}' (-32602)"
                    )

            # Return completions based on the input
            return {
                "result": {
                    "completion": {
                        "values": [
                            f"{arg_value}ample",
                            f"{arg_value}pert",
                            f"{arg_value}cellent",
                        ],
                        "hasMore": False,
                    }
                }
            }
        elif ref_type == "ref/resource":
            # Handle resource URI completion
            uri = ref.get("uri")
            arg_name = argument.get("name")
            arg_value = argument.get("value", "")

            # Return completions based on the input
            return {
                "result": {
                    "completion": {
                        "values": [
                            f"{arg_value}file1.txt",
                            f"{arg_value}file2.json",
                            f"{arg_value}directory/",
                        ],
                        "hasMore": False,
                    }
                }
            }
        else:
            raise ValueError(
                f"Invalid params: unsupported ref type {ref_type} (-32602)"
            )


@pytest.fixture
def client():
    """Provides a client for interacting with MCP servers."""
    return MockMCPClient()
