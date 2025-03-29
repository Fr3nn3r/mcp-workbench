import pytest


@pytest.mark.mcp_requirement(feature="completion/complete", level="MUST")
def test_prompt_argument_completion_returns_suggestions(client, spec_version):
    """Test that completion/complete returns valid suggestions for prompt arguments."""
    # Check server capabilities
    caps = client.get_capabilities()
    if not caps.get("completion", {}).get("complete"):
        pytest.skip("Server does not support completion/complete")

    # Find a prompt with arguments
    prompts = client.send("prompts/list")["result"]["prompts"]
    prompt = next((p for p in prompts if p.get("arguments")), None)
    if not prompt:
        pytest.skip("No prompts with arguments available")

    # Use the first argument for testing
    arg_name = prompt["arguments"][0]["name"]

    # Call completion/complete with a partial input
    result = client.send(
        "completion/complete",
        {
            "ref": {"type": "ref/prompt", "name": prompt["name"]},
            "argument": {"name": arg_name, "value": "e"},  # simulate partial input
        },
    )

    # Verify the response structure
    completion = result["result"]["completion"]
    assert isinstance(completion["values"], list), "values must be a list"
    assert len(completion["values"]) <= 100, "must not return more than 100 suggestions"
    assert isinstance(completion["hasMore"], bool), "hasMore must be a boolean"

    # Optional total field
    if "total" in completion:
        assert isinstance(
            completion["total"], int
        ), "total must be an integer if present"


@pytest.mark.mcp_requirement(feature="completion/complete", level="MUST")
def test_prompt_argument_completion_invalid_prompt(client, spec_version):
    """Test that completion/complete fails with error for invalid prompt."""
    # Skip if server doesn't support completion
    caps = client.get_capabilities()
    if not caps.get("completion", {}).get("complete"):
        pytest.skip("Server does not support completion/complete")

    # Try to get completions for a non-existent prompt
    with pytest.raises(Exception) as exc_info:
        client.send(
            "completion/complete",
            {
                "ref": {"type": "ref/prompt", "name": "non_existent_prompt"},
                "argument": {"name": "arg", "value": "test"},
            },
        )

    # Check for the expected error code/message
    error_msg = str(exc_info.value)
    assert any(
        err in error_msg for err in ["-32602", "Invalid params", "unknown prompt"]
    ), f"Expected invalid params error, got: {error_msg}"


@pytest.mark.mcp_requirement(feature="completion/complete", level="MUST")
def test_prompt_argument_completion_invalid_argument(client, spec_version):
    """Test that completion/complete fails with error for invalid argument."""
    # Skip if server doesn't support completion
    caps = client.get_capabilities()
    if not caps.get("completion", {}).get("complete"):
        pytest.skip("Server does not support completion/complete")

    # Find a prompt with arguments
    prompts = client.send("prompts/list")["result"]["prompts"]
    prompt = next((p for p in prompts if p.get("arguments")), None)
    if not prompt:
        pytest.skip("No prompts with arguments available")

    # Try to get completions for a non-existent argument
    with pytest.raises(Exception) as exc_info:
        client.send(
            "completion/complete",
            {
                "ref": {"type": "ref/prompt", "name": prompt["name"]},
                "argument": {"name": "non_existent_arg", "value": "test"},
            },
        )

    # Check for the expected error code/message
    error_msg = str(exc_info.value)
    assert any(
        err in error_msg for err in ["-32602", "Invalid params", "unknown argument"]
    ), f"Expected invalid params error, got: {error_msg}"
