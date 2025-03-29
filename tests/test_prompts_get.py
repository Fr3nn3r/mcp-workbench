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


@pytest.mark.mcp_requirement(feature="prompts/get", level="SHOULD")
def test_prompts_get_internal_error_fails(client, spec_version):
    """Test that internal server errors are reported with the correct error code."""
    # Attempt to trigger an internal server error
    with pytest.raises(Exception) as exc_info:
        client.send("prompts/get", {"name": "cause_internal_error", "arguments": {}})

    # Validate error code for internal error
    error_msg = str(exc_info.value)
    assert "-32603" in error_msg, f"Expected internal error code, got: {error_msg}"


@pytest.mark.mcp_requirement(feature="prompts", level="MUST")
def test_prompts_capability_declared(client, spec_version):
    """Test that the server declares the prompts capability."""
    # Check if the prompts capability is declared
    caps = client.get_capabilities()
    assert "prompts" in caps, "Server must declare prompts capability"

    # Optional deeper checks for specific endpoints
    if "prompts" in caps:
        prompts_caps = caps["prompts"]
        assert prompts_caps.get("list") is True, "Server must support prompts/list"
        assert prompts_caps.get("get") is True, "Server must support prompts/get"


@pytest.mark.mcp_requirement(feature="prompts/get", level="SHOULD")
def test_prompts_get_rejects_injection_strings(client, spec_version):
    """Test that the server safely handles potentially malicious input strings."""
    # Find a prompt with arguments
    prompts = client.send("prompts/list")["result"]["prompts"]
    prompt = next((p for p in prompts if p.get("arguments")), None)
    if not prompt:
        pytest.skip("No prompt with arguments")

    # Prepare a potentially malicious argument
    injection_string = "'; DROP TABLE users; --"
    args = {prompt["arguments"][0]["name"]: injection_string}

    # Call prompts/get with the suspicious input
    result = client.send("prompts/get", {"name": prompt["name"], "arguments": args})

    # Expect it to handle the input safely (no crashes or exceptions)
    assert "result" in result, "Server should safely process suspicious input"

    # Optional check: verify the input was sanitized or encoded correctly
    # This is implementation specific, but we can check if it was included without modification
    assert PromptsGetResult(**result["result"]), "Response should have valid structure"
