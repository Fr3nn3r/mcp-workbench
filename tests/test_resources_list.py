import pytest
from mcp.protocol import ResourcesListResult


@pytest.mark.mcp_requirement(feature="resources/list", level="MUST")
def test_resources_list_returns_valid_structure(client, spec_version):
    """Test that resources/list returns a valid structure with required fields."""
    result = client.send("resources/list")
    parsed = ResourcesListResult(**result["result"])

    # Validate the resources list is present and non-empty
    assert isinstance(parsed.resources, list)
    assert len(parsed.resources) > 0

    # Validate structure of each resource
    for res in parsed.resources:
        # Required fields
        assert isinstance(res.uri, str)
        assert isinstance(res.name, str)

        # Optional field
        if res.mimeType:
            assert isinstance(res.mimeType, str)

    # Optional pagination cursor
    if parsed.nextCursor:
        assert isinstance(parsed.nextCursor, str)
