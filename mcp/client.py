"""MCP client implementation."""

import json
import logging
import requests
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class MCPError(Exception):
    """Base class for MCP errors."""

    pass


class JSONRPCError(MCPError):
    """JSON-RPC error response."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"JSON-RPC error {code}: {message}")


class MCPClient:
    """Client for interacting with an MCP server."""

    def __init__(self, server_url: str):
        """Initialize the client.

        Args:
            server_url: URL of the MCP server
        """
        self.server_url = server_url
        self.request_id = 0

    def send(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Send a JSON-RPC request to the server.

        Args:
            method: The method name to call
            params: Optional parameters for the method

        Returns:
            The result from the method call

        Raises:
            JSONRPCError: If the server returns a JSON-RPC error
            MCPError: For other errors
        """
        self.request_id += 1
        request = {"jsonrpc": "2.0", "method": method, "id": self.request_id}
        if params:
            request["params"] = params

        try:
            logger.debug(f"Sending request to {self.server_url}: {request}")
            response = requests.post(self.server_url, json=request)
            data = response.json()
            logger.debug(f"Received response: {data}")

            if "error" in data:
                error = data["error"]
                raise JSONRPCError(error["code"], error["message"])

            if "result" not in data:
                raise MCPError("Invalid response: missing 'result' field")

            return data["result"]

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise MCPError(f"Request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise MCPError(f"Invalid JSON response: {e}")
        except KeyError as e:
            logger.error(f"Invalid response format: {e}")
            raise MCPError(f"Invalid response format: {e}")
