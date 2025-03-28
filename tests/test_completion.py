"""Test cases for completion/complete endpoint."""

import pytest
from mcp.client import JSONRPCError
from mcp.protocol.schema import CompletionResult


@pytest.mark.mcp_requirement(
    feature="completion/complete", level="MUST", req_id="COMPLETION-1"
)
def test_prompt_argument_completion(client):
    """Test completion for prompt arguments."""
    # Get a prompt with arguments
    prompt_list = client.send("prompts/list")["result"]["prompts"]
    prompt = next((p for p in prompt_list if p.get("arguments")), None)
    if not prompt:
        pytest.skip("No prompt with arguments")

    arg = prompt["arguments"][0]["name"]
    result = client.send(
        "completion/complete",
        {
            "ref": {"type": "ref/prompt", "name": prompt["name"]},
            "argument": {"name": arg, "value": "ex"},
        },
    )
    parsed = CompletionResult(**result["result"])

    assert "values" in parsed.completion, "Must return completion values"
    assert isinstance(parsed.completion["values"], list), "Values must be a list"
    assert "hasMore" in parsed.completion, "Must indicate if more values exist"
    assert isinstance(parsed.completion["hasMore"], bool), "hasMore must be boolean"


@pytest.mark.mcp_requirement(
    feature="completion/complete", level="MUST", req_id="COMPLETION-2"
)
def test_resource_uri_completion(client):
    """Test completion for resource URIs."""
    # Get a resource template
    templates = client.send("resources/templates/list")["result"]["resourceTemplates"]
    if not templates:
        pytest.skip("No resource templates available")

    template = templates[0]
    result = client.send(
        "completion/complete",
        {
            "ref": {"type": "ref/resource", "uri": template["uriTemplate"]},
            "value": "ex",
        },
    )
    parsed = CompletionResult(**result["result"])

    assert "values" in parsed.completion, "Must return completion values"
    assert isinstance(parsed.completion["values"], list), "Values must be a list"
    assert "hasMore" in parsed.completion, "Must indicate if more values exist"
    assert isinstance(parsed.completion["hasMore"], bool), "hasMore must be boolean"


@pytest.mark.mcp_requirement(
    feature="completion/complete", level="MUST", req_id="COMPLETION-3"
)
def test_completion_error_cases(client):
    """Test error handling for completion requests."""
    # Test invalid reference type
    with pytest.raises(JSONRPCError) as exc:
        client.send(
            "completion/complete",
            {"ref": {"type": "invalid", "name": "test"}, "value": "test"},
        )
    assert exc.value.code == -32602, "Should return invalid params error"

    # Test missing required fields
    with pytest.raises(JSONRPCError) as exc:
        client.send("completion/complete", {"ref": {"type": "ref/prompt"}})
    assert exc.value.code == -32602, "Should return invalid params error"

    # Test invalid prompt name
    with pytest.raises(JSONRPCError) as exc:
        client.send(
            "completion/complete",
            {
                "ref": {"type": "ref/prompt", "name": "nonexistent"},
                "argument": {"name": "test", "value": "test"},
            },
        )
    assert exc.value.code == -32602, "Should return invalid params error"
