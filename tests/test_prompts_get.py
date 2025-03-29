import pytest
from mcp.protocol import PromptsGetResult


@pytest.mark.mcp_requirement(feature="prompts/get", level="MUST")
def test_prompts_get_returns_valid_prompt(client, spec_version):
    """Test that prompts/get returns a valid prompt structure."""
    # Get available prompts from prompts/list
    prompts = client.send("prompts/list")["result"]["prompts"]
    if not prompts:
        pytest.skip("No prompts available")

    prompt = prompts[0]

    # Prepare arguments for required params
    args = {}
    for arg in prompt.get("arguments", []):
        if arg["required"]:
            args[arg["name"]] = "example input"

    # Call prompts/get
    response = client.send("prompts/get", {"name": prompt["name"], "arguments": args})

    # Validate the response
    result = PromptsGetResult(**response["result"])

    # MUST: at least one message
    assert isinstance(result.messages, list)
    assert len(result.messages) > 0

    for message in result.messages:
        # MUST: valid role
        assert message.role in ("user", "assistant")

        # MUST: content has valid type
        content = message.content
        assert content.type in ("text", "image", "resource")

        # Validate content based on type
        if content.type == "text":
            assert isinstance(content.text, str)
        elif content.type == "image":
            assert isinstance(content.data, str)
            assert isinstance(content.mimeType, str)
        elif content.type == "resource":
            resource = content.resource
            assert "uri" in resource and "mimeType" in resource
            assert "text" in resource or "blob" in resource


@pytest.mark.mcp_requirement(feature="prompts/get", level="MUST")
def test_prompts_get_fails_on_missing_required_arg(client, spec_version):
    """Test that prompts/get fails correctly when missing required arguments."""
    # Find a prompt with required arguments
    prompts = client.send("prompts/list")["result"]["prompts"]
    prompt = next((p for p in prompts if p.get("arguments")), None)

    if not prompt or not any(arg["required"] for arg in prompt.get("arguments", [])):
        pytest.skip("No prompt with required arguments")

    # Try to call without providing required arguments
    with pytest.raises(Exception) as exc_info:
        client.send(
            "prompts/get",
            {"name": prompt["name"], "arguments": {}},  # required args missing
        )

    # Validate error
    error_msg = str(exc_info.value)
    assert "-32602" in error_msg or "Invalid params" in error_msg


@pytest.mark.mcp_requirement(feature="prompts/get", level="MUST")
def test_prompts_get_fails_on_invalid_prompt_name(client, spec_version):
    """Test that prompts/get fails correctly with invalid prompt name."""
    with pytest.raises(Exception) as exc_info:
        client.send("prompts/get", {"name": "non_existent_prompt", "arguments": {}})

    # Validate error
    error_msg = str(exc_info.value)
    assert "-32602" in error_msg or "Invalid params" in error_msg
