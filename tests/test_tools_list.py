import pytest
from mcp.protocol import ToolsListResult


@pytest.mark.mcp_requirement(feature="tools/list", level="MUST")
def test_tools_list_returns_valid_tools(client, spec_version):
    """Test that tools/list returns valid tool definitions with required fields."""
    # Call the tools/list endpoint
    result = client.send("tools/list")
    parsed = ToolsListResult(**result["result"])

    # Validate that tools is a non-empty list
    assert isinstance(parsed.tools, list), "tools must be a list"
    assert len(parsed.tools) > 0, "tools list must not be empty"

    # Validate the structure of each tool
    for tool in parsed.tools:
        # Required fields
        assert isinstance(tool.name, str), f"Tool name must be a string: {tool.name}"
        assert isinstance(
            tool.description, str
        ), f"Tool description must be a string: {tool.description}"
        assert isinstance(
            tool.inputSchema, dict
        ), f"Tool inputSchema must be a dict: {tool.inputSchema}"

        # Minimal schema validation
        if tool.inputSchema:
            assert "type" in tool.inputSchema, "inputSchema must have a 'type' field"
            if "properties" in tool.inputSchema:
                assert isinstance(
                    tool.inputSchema["properties"], dict
                ), "properties must be a dict"

    # Optional pagination cursor
    if parsed.nextCursor:
        assert isinstance(
            parsed.nextCursor, str
        ), "nextCursor must be a string if present"
