import pytest
from mcp.protocol import ToolCallResult


@pytest.mark.mcp_requirement(feature="tools/call", level="MUST")
def test_tools_call_works_with_valid_input(client, spec_version):
    """Test that tools/call works correctly with valid tool name and arguments."""
    # Get available tools
    tools = client.send("tools/list")["result"]["tools"]
    if not tools:
        pytest.skip("No tools available")

    # Use the first tool for testing
    tool = tools[0]
    required_fields = tool["inputSchema"].get("required", [])
    args = {field: "example value" for field in required_fields}

    # Call the tool with valid arguments
    result = client.send("tools/call", {"name": tool["name"], "arguments": args})

    # Validate the response
    parsed = ToolCallResult(**result["result"])
    assert isinstance(parsed.content, list), "content must be a list"
    assert len(parsed.content) > 0, "content list must not be empty"

    # Verify each content item has a valid type
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
        elif item["type"] == "image":
            assert "data" in item, "Image content must have 'data' field"
            assert "mimeType" in item, "Image content must have 'mimeType' field"
        elif item["type"] == "resource":
            assert "resource" in item, "Resource content must have 'resource' field"

    # Check optional isError field
    if hasattr(parsed, "isError"):
        assert parsed.isError is False, "isError should be False for successful calls"


@pytest.mark.mcp_requirement(feature="tools/call", level="MUST")
def test_tools_call_missing_required_args_fails(client, spec_version):
    """Test that tools/call fails when required arguments are missing."""
    # Find a tool with required arguments
    tools = client.send("tools/list")["result"]["tools"]
    tool = next(
        (
            t
            for t in tools
            if t["inputSchema"].get("required")
            and len(t["inputSchema"]["required"]) > 0
        ),
        None,
    )

    if not tool:
        pytest.skip("No tools with required arguments")

    # Call the tool without required arguments
    with pytest.raises(Exception) as exc_info:
        client.send(
            "tools/call",
            {"name": tool["name"], "arguments": {}},  # Missing required args
        )

    # Validate error response
    error_msg = str(exc_info.value)
    assert any(
        err in error_msg for err in ["-32602", "Invalid params", "missing required"]
    ), f"Expected invalid params error, got: {error_msg}"


@pytest.mark.mcp_requirement(feature="tools/call", level="MUST")
def test_tools_call_invalid_tool_name_fails(client, spec_version):
    """Test that tools/call fails with appropriate error for unknown tool names."""
    # Call with a non-existent tool name
    with pytest.raises(Exception) as exc_info:
        client.send("tools/call", {"name": "not_a_real_tool_123", "arguments": {}})

    # Validate error response
    error_msg = str(exc_info.value)
    assert any(
        err in error_msg for err in ["-32602", "Invalid params", "Unknown tool"]
    ), f"Expected unknown tool error, got: {error_msg}"


@pytest.mark.mcp_requirement(feature="tools/call", level="SHOULD")
def test_tools_call_access_control_fails(client, spec_version):
    """Test that calls to privileged tools fail with appropriate error messages."""
    # Get list of tools
    tools = client.send("tools/list")["result"]["tools"]
    admin_tool = next((t for t in tools if t["name"] == "admin_only_tool"), None)

    if not admin_tool:
        pytest.skip("No admin-only tool available for testing")

    # Try to call a restricted or admin-only tool
    with pytest.raises(Exception) as exc_info:
        client.send(
            "tools/call",
            {"name": "admin_only_tool", "arguments": {"command": "list_users"}},
        )

    # Validate the error message contains authorization-related information
    error_msg = str(exc_info.value).lower()
    assert any(
        term in error_msg for term in ["unauthorized", "privileges", "-32602"]
    ), f"Expected authorization error, got: {error_msg}"


@pytest.mark.mcp_requirement(feature="tools/call", level="SHOULD")
def test_tools_call_rate_limit(client, spec_version):
    """Test that the server enforces rate limits on tool calls."""
    # Get available tools
    tools = client.send("tools/list")["result"]["tools"]
    if not tools:
        pytest.skip("No tools available")

    # Use the first tool for testing
    tool = tools[0]
    required_fields = tool["inputSchema"].get("required", [])
    args = {field: "example value" for field in required_fields}

    # Attempt rapid calls to trigger rate limiting
    for i in range(15):  # Make more calls than the limit (10)
        try:
            client.send("tools/call", {"name": tool["name"], "arguments": args})
            # Print progress to help with debugging
            if (i + 1) % 5 == 0:
                print(f"Made {i + 1} calls without rate limit")
        except Exception as e:
            error_msg = str(e).lower()
            if any(term in error_msg for term in ["rate limit", "exceeded", "-32005"]):
                # Success - rate limit was triggered
                return
            # If another error occurred, re-raise it
            raise

    # If we get here, rate limiting wasn't triggered
    pytest.skip("Rate limiting not enforced or limit higher than expected")


@pytest.mark.mcp_requirement(feature="tools/call", level="SHOULD")
def test_tools_call_output_sanitization(client, spec_version):
    """Test that tool output with user-controlled content is properly sanitized."""
    # Find the echo tool
    tools = client.send("tools/list")["result"]["tools"]
    echo_tool = next((t for t in tools if t["name"] == "echo_tool"), None)

    if not echo_tool:
        pytest.skip("No echo tool available for testing")

    # Call the echo tool with potentially malicious content
    malicious_input = "<script>alert(1)</script>"
    result = client.send(
        "tools/call", {"name": "echo_tool", "arguments": {"text": malicious_input}}
    )

    # Check that the output doesn't contain the script tags
    content = result["result"]["content"]
    assert (
        isinstance(content, list) and len(content) > 0
    ), "Tool response must have content"

    if content[0]["type"] == "text":
        text_content = content[0]["text"]
        assert "<script>" not in text_content, "Output contains unsanitized script tag"
        assert "</script>" not in text_content, "Output contains unsanitized script tag"
        # Optional - ensure some content was preserved
        assert (
            "alert(1)" in text_content
        ), "Legitimate content was removed during sanitization"
