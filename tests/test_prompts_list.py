"""Test cases for prompts/list endpoint."""

import pytest
from mcp.client import JSONRPCError


@pytest.mark.mcp_requirement(
    feature="prompts/list", level="MUST", req_id="PROMPTS-LIST-1"
)
def test_prompts_list_basic(client):
    """Test that prompts/list returns a valid list of prompts."""
    result = client.send("prompts/list")
    assert "prompts" in result, "Response must contain 'prompts' field"
    assert isinstance(result["prompts"], list), "Prompts must be a list"

    # Validate each prompt has required fields
    for prompt in result["prompts"]:
        assert isinstance(prompt, dict), "Each prompt must be a dictionary"
        assert "name" in prompt, "Each prompt must have a name"
        assert isinstance(prompt["name"], str), "Prompt name must be a string"


@pytest.mark.mcp_requirement(
    feature="prompts/list", level="SHOULD", req_id="PROMPTS-LIST-3"
)
def test_prompts_list_pagination(client):
    """Test that prompts/list supports pagination."""
    # Request first page
    result = client.send("prompts/list", {"use_pagination": True})
    assert "prompts" in result, "Response must contain 'prompts' field"
    assert isinstance(result["prompts"], list), "Prompts must be a list"
    assert "nextCursor" in result, "First page should have nextCursor"

    # Request second page
    next_result = client.send("prompts/list", {"cursor": result["nextCursor"]})
    assert "prompts" in next_result, "Response must contain 'prompts' field"
    assert isinstance(next_result["prompts"], list), "Prompts must be a list"

    # Verify we got different prompts
    assert (
        result["prompts"] != next_result["prompts"]
    ), "Pages should contain different prompts"


@pytest.mark.mcp_requirement(
    feature="prompts/list", level="MUST", req_id="PROMPTS-LIST-2"
)
def test_prompts_list_error_cases(client):
    """Test error handling for prompts/list."""
    # Test with invalid cursor
    with pytest.raises(JSONRPCError) as exc_info:
        client.send("prompts/list", {"cursor": "invalid_cursor"})
    assert (
        exc_info.value.code == -32602
    ), "Should return invalid params error for invalid cursor"
