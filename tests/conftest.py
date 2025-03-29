import pytest
from unittest.mock import MagicMock
import time


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
        }
        self.prompt_list_changes = False
        self._change_timer = 0

    def send(self, method, params=None):
        """Simulate sending a request to an MCP server."""
        if method == "prompts/get":
            return self._handle_prompts_get(params or {})

        if method == "resources/read":
            return self._handle_resources_read(params or {})

        if method == "resources/subscribe":
            return self._handle_resources_subscribe(params or {})

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

    def _handle_prompts_get(self, params):
        """Handle prompts/get requests with validation."""
        name = params.get("name")
        arguments = params.get("arguments", {})

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


@pytest.fixture
def client():
    """Provides a client for interacting with MCP servers."""
    return MockMCPClient()
