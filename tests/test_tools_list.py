"""Test cases for tools/list endpoint."""

import pytest
from mcp.client import JSONRPCError
from mcp.protocol.schema import ToolsListResult


@pytest.mark.mcp_requirement(feature="tools/list", level="MUST", req_id="TOOLS-LIST-1")
def test_tools_list_returns_valid_tools(client):
    """Test that tools/list returns valid tools with required fields."""
    result = client.send("tools/list")
    parsed = ToolsListResult(**result["result"])

    # Validate each tool
    for tool in parsed.tools:
        assert isinstance(tool.name, str), "Tool name must be a string"
        assert isinstance(tool.description, str), "Tool description must be a string"
        assert isinstance(tool.inputSchema, dict), "Tool schema must be a dict"


@pytest.mark.mcp_requirement(
    feature="tools/list", level="SHOULD", req_id="TOOLS-LIST-2"
)
def test_tools_list_pagination(client):
    """Test that tools/list supports pagination if nextCursor is present."""
    result = client.send("tools/list")
    first_page = ToolsListResult(**result["result"])

    if not first_page.nextCursor:
        pytest.skip("Pagination not supported")

    # Get second page
    result = client.send("tools/list", {"cursor": first_page.nextCursor})
    second_page = ToolsListResult(**result["result"])

    # Verify pages are different
    first_tools = {t.name for t in first_page.tools}
    second_tools = {t.name for t in second_page.tools}
    assert first_tools != second_tools, "Second page must return different tools"


@pytest.mark.mcp_requirement(feature="tools/list", level="MUST", req_id="TOOLS-LIST-3")
def test_tools_list_error_cases(client):
    """Test error handling for tools/list."""
    # Test with invalid cursor
    with pytest.raises(JSONRPCError) as exc:
        client.send("tools/list", {"cursor": "invalid-cursor"})
    assert exc.value.code == -32602, "Should return invalid params error"
