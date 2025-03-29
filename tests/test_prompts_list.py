import pytest
from mcp.protocol import PromptsListResult


@pytest.mark.mcp_requirement(feature="prompts/list", level="MUST")
def test_prompts_list_returns_valid_structure(client, spec_version):
    """Test that prompts/list returns a valid structure according to the spec."""
    response = client.send("prompts/list")
    result = PromptsListResult(**response["result"])  # Validates schema

    # MUST: non-empty list of prompts
    assert isinstance(result.prompts, list)
    assert len(result.prompts) > 0

    for prompt in result.prompts:
        # MUST: name must exist
        assert isinstance(prompt.name, str)

        # OPTIONAL: description
        if prompt.description:
            assert isinstance(prompt.description, str)

        # OPTIONAL: arguments
        if prompt.arguments:
            for arg in prompt.arguments:
                assert isinstance(arg.name, str)
                assert isinstance(arg.description, str)
                assert isinstance(arg.required, bool)

    # SHOULD: nextCursor is string if present
    if result.nextCursor:
        assert isinstance(result.nextCursor, str)
