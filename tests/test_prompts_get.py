"""Test cases for prompts/get endpoint."""

import pytest
from mcp.client import JSONRPCError


@pytest.mark.mcp_requirement(
    feature="prompts/get", level="MUST", req_id="PROMPTS-GET-3"
)
def test_prompts_get_returns_valid_messages(client):
    """Test that prompts/get returns valid message structure."""
    result = client.send(
        "prompts/get", {"name": "chat", "arguments": {"messages": "test"}}
    )

    assert "description" in result, "Response must contain description"
    assert "messages" in result, "Response must contain messages"
    assert isinstance(result["messages"], list), "Messages must be a list"

    for msg in result["messages"]:
        assert "role" in msg, "Each message must have a role"
        assert "content" in msg, "Each message must have content"
        assert isinstance(msg["content"], dict), "Content must be a dictionary"
        assert "type" in msg["content"], "Content must have a type"


@pytest.mark.mcp_requirement(
    feature="prompts/get", level="MUST", req_id="PROMPTS-GET-2"
)
def test_prompts_get_missing_argument_raises_error(client):
    """Test that prompts/get validates required arguments."""
    with pytest.raises(JSONRPCError) as exc_info:
        client.send("prompts/get", {"name": "chat"})
    assert (
        exc_info.value.code == -32602
    ), "Should return invalid params error for missing argument"
    assert "messages" in str(
        exc_info.value
    ), "Error should mention missing argument name"


@pytest.mark.mcp_requirement(
    feature="prompts/get", level="MUST", req_id="PROMPTS-GET-1"
)
def test_prompts_get_invalid_prompt_name(client):
    """Test that prompts/get validates prompt name."""
    with pytest.raises(JSONRPCError) as exc_info:
        client.send(
            "prompts/get", {"name": "invalid_prompt", "arguments": {"messages": "test"}}
        )
    assert (
        exc_info.value.code == -32602
    ), "Should return invalid params error for invalid prompt name"


@pytest.mark.mcp_requirement(
    feature="prompts/get", level="MUST", req_id="PROMPTS-GET-2"
)
def test_prompts_get_invalid_argument_type(client):
    """Test that prompts/get validates argument types."""
    with pytest.raises(JSONRPCError) as exc_info:
        client.send(
            "prompts/get",
            {"name": "chat", "arguments": {"messages": 123}},  # Should be string
        )
    assert (
        exc_info.value.code == -32602
    ), "Should return invalid params error for invalid argument type"


@pytest.mark.mcp_requirement(
    feature="prompts/get", level="MUST", req_id="PROMPTS-GET-3"
)
def test_prompts_get_content_type_validation(client):
    """Test that prompts/get validates content types."""
    result = client.send(
        "prompts/get", {"name": "chat", "arguments": {"messages": "test"}}
    )

    # Verify each message has valid content type
    for msg in result["messages"]:
        content = msg["content"]
        assert content["type"] in [
            "text",
            "image",
            "resource",
        ], "Content type must be valid"

        if content["type"] == "text":
            assert "text" in content, "Text content must have text field"
            assert isinstance(content["text"], str), "Text field must be string"

        elif content["type"] == "image":
            assert "data" in content, "Image content must have data field"
            assert "mimeType" in content, "Image content must have mimeType"
            assert content["mimeType"].startswith(
                "image/"
            ), "Image mimeType must be valid"

        elif content["type"] == "resource":
            assert "resource" in content, "Resource content must have resource object"
            resource = content["resource"]
            assert "uri" in resource, "Resource must have URI"
            assert "mimeType" in resource, "Resource must have mimeType"
            assert "text" in resource, "Resource must have text description"
