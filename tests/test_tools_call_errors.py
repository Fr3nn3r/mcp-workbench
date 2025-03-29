import pytest
from mcp.protocol import ToolCallResult


@pytest.mark.mcp_requirement(feature="tools/call", level="SHOULD")
def test_tools_call_returns_error_flag(client, spec_version):
    """Test that tools/call returns isError: true when a tool fails internally."""
    # Get the list of available tools
    tools = client.send("tools/list")["result"]["tools"]

    # Find a tool that we know can produce errors
    error_tool = next((t for t in tools if "error" in t["name"].lower()), None)
    if not error_tool:
        pytest.skip("No known error-producing tool exposed")

    # Prepare arguments that will trigger an error
    required = error_tool["inputSchema"].get("required", [])
    args = {k: "trigger error" for k in required}

    # Call the tool, expecting it to fail internally but return a valid response
    result = client.send("tools/call", {"name": error_tool["name"], "arguments": args})

    # Parse and validate the response
    parsed = ToolCallResult(**result["result"])

    # Primary assertion: should have isError: true
    assert parsed.isError is True, "Failed tool execution should set isError: true"

    # Secondary assertions: response should still be well-formed
    assert isinstance(
        parsed.content, list
    ), "Content should still be a list despite the error"
    assert len(parsed.content) > 0, "Content should not be empty even for errors"

    # Optional but helpful: check that error message is informative
    msg = parsed.content[0]
    if msg["type"] == "text":
        error_text = msg["text"].lower()
        assert any(
            term in error_text for term in ["error", "fail", "exception"]
        ), "Error message should contain informative terms"


@pytest.mark.mcp_requirement(feature="tools/call", level="MUST")
def test_tools_call_error_content_is_valid(client, spec_version):
    """Test that tools/call error responses contain valid content structures."""
    # Find the error tool
    tools = client.send("tools/list")["result"]["tools"]
    error_tool = next((t for t in tools if "error" in t["name"].lower()), None)
    if not error_tool:
        pytest.skip("No known error-producing tool exposed")

    # Prepare arguments to trigger an error
    required = error_tool["inputSchema"].get("required", [])
    args = {k: "trigger error" for k in required}

    # Call the tool
    result = client.send("tools/call", {"name": error_tool["name"], "arguments": args})

    # Validate response structure
    parsed = ToolCallResult(**result["result"])

    # Content format should follow the same rules as success responses
    for item in parsed.content:
        assert "type" in item, "Each content item must have a type field"
        assert item["type"] in [
            "text",
            "image",
            "resource",
        ], f"Invalid content type: {item['type']}"

        # Type-specific validation
        if item["type"] == "text":
            assert "text" in item, "Text content must have 'text' field"
            assert isinstance(item["text"], str), "Text field must be a string"
        elif item["type"] == "image":
            assert "data" in item, "Image content must have 'data' field"
            assert "mimeType" in item, "Image content must have 'mimeType' field"
        elif item["type"] == "resource":
            assert "resource" in item, "Resource content must have 'resource' field"
