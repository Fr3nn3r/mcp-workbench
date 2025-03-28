"""Test cases for tools/call endpoint."""

import pytest
from mcp.client import JSONRPCError
from mcp.protocol.schema import ToolCallResult


@pytest.mark.mcp_requirement(feature="tools/call", level="MUST", req_id="TOOLS-CALL-1")
def test_tools_call_executes_successfully(client):
    """Test that tools/call executes a tool and returns valid result."""
    # Get available tools
    tools = client.send("tools/list")["result"]["tools"]
    if not tools:
        pytest.skip("No tools available")

    tool = tools[0]
    # Build dummy arguments based on schema
    args = {key: "test" for key in tool["inputSchema"].get("required", [])}

    result = client.send("tools/call", {"name": tool["name"], "arguments": args})
    parsed = ToolCallResult(**result["result"])

    # Validate result content
    assert len(parsed.content) > 0, "Tool result must contain content"
    for item in parsed.content:
        assert item.type in {"text", "image", "resource_text", "resource_blob"}


@pytest.mark.mcp_requirement(feature="tools/call", level="MUST", req_id="TOOLS-CALL-2")
def test_tools_call_error_cases(client):
    """Test error handling for tools/call."""
    # Test with unknown tool
    with pytest.raises(JSONRPCError) as exc:
        client.send("tools/call", {"name": "nonexistent_tool", "arguments": {}})
    assert exc.value.code == -32602, "Should return invalid params error"

    # Get a real tool to test invalid arguments
    tools = client.send("tools/list")["result"]["tools"]
    if not tools:
        pytest.skip("No tools available")

    tool = tools[0]
    # Send invalid arguments
    with pytest.raises(JSONRPCError) as exc:
        client.send(
            "tools/call", {"name": tool["name"], "arguments": {"invalid_arg": "test"}}
        )
    assert exc.value.code == -32602, "Should return invalid params error"


@pytest.mark.mcp_requirement(
    feature="tools/call", level="SHOULD", req_id="TOOLS-CALL-3"
)
def test_tools_call_execution_error(client):
    """Test that tool execution errors are properly reported."""
    tools = client.send("tools/list")["result"]["tools"]
    if not tools:
        pytest.skip("No tools available")

    tool = tools[0]
    # Try to trigger an execution error (implementation specific)
    result = client.send(
        "tools/call",
        {
            "name": tool["name"],
            "arguments": {k: "" for k in tool["inputSchema"].get("required", [])},
        },
    )
    parsed = ToolCallResult(**result["result"])

    if parsed.isError:
        assert len(parsed.content) > 0, "Error result must contain error message"
        assert any(
            c.type == "text" for c in parsed.content
        ), "Error should include text message"
