"""Test cases for resources/list endpoint."""

import pytest
from mcp.client import JSONRPCError
from mcp.protocol.schema import ResourcesListResult


@pytest.mark.mcp_requirement(
    feature="resources/list", level="MUST", req_id="RESOURCES-LIST-1"
)
def test_resources_list_returns_valid_structure(client):
    """Test that resources/list returns a valid list of resources."""
    result = client.send("resources/list")
    parsed = ResourcesListResult(**result)

    assert isinstance(parsed.resources, list), "Response must contain resources array"
    for res in parsed.resources:
        assert isinstance(res.uri, str), "Resource URI must be a string"
        assert isinstance(res.name, str), "Resource name must be a string"
        if res.mimeType:
            assert isinstance(res.mimeType, str), "Resource mimeType must be a string"


@pytest.mark.mcp_requirement(
    feature="resources/list", level="SHOULD", req_id="RESOURCES-LIST-2"
)
def test_resources_list_pagination(client):
    """Test that resources/list supports pagination."""
    # Request first page
    result = client.send("resources/list", {"use_pagination": True})
    parsed = ResourcesListResult(**result)

    assert isinstance(parsed.resources, list), "Response must contain resources array"
    if not parsed.nextCursor:
        pytest.skip("Server does not support pagination or has no more pages")

    # Request second page
    next_result = client.send("resources/list", {"cursor": parsed.nextCursor})
    next_parsed = ResourcesListResult(**next_result)

    assert isinstance(
        next_parsed.resources, list
    ), "Second page must contain resources array"
    # Verify we got different resources
    assert (
        parsed.resources != next_parsed.resources
    ), "Pages should contain different resources"


@pytest.mark.mcp_requirement(
    feature="resources/list", level="MUST", req_id="RESOURCES-LIST-3"
)
def test_resources_list_error_cases(client):
    """Test error handling for resources/list."""
    # Test with invalid cursor
    with pytest.raises(JSONRPCError) as exc_info:
        client.send("resources/list", {"cursor": "invalid_cursor"})
    assert (
        exc_info.value.code == -32602
    ), "Should return invalid params error for invalid cursor"

    # Test with invalid pagination parameters
    with pytest.raises(JSONRPCError) as exc_info:
        client.send("resources/list", {"use_pagination": "not_a_bool"})
    assert (
        exc_info.value.code == -32602
    ), "Should return invalid params error for invalid pagination type"
