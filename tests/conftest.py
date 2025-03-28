"""Test fixtures for MCP test suite."""

import pytest
from mcp.client import MCPClient


def pytest_addoption(parser):
    """Add command-line options for the test suite."""
    parser.addoption(
        "--server-url", required=True, help="Base URL of the MCP server to test"
    )


@pytest.fixture
def server_url(request):
    """Get the server URL from command line options."""
    return request.config.getoption("--server-url")


@pytest.fixture
def client(server_url):
    """Create a reusable JSON-RPC client."""
    return MCPClient(server_url)
