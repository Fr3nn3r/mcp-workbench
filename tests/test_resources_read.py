"""Test cases for resources/read endpoint."""

import pytest
from mcp.client import JSONRPCError
from mcp.protocol.schema import ResourcesReadResult


@pytest.mark.mcp_requirement(
    feature="resources/read", level="MUST", req_id="RESOURCES-READ-1"
)
def test_resources_read_returns_content(client):
    """Test that resources/read returns valid content."""
    # First get a list of resources
    resources = client.send("resources/list")
    if not resources["resources"]:
        pytest.skip("No resources available")

    # Try to read the first resource
    uri = resources["resources"][0]["uri"]
    result = client.send("resources/read", {"uri": uri})
    parsed = ResourcesReadResult(**result)

    # Validate content structure
    assert len(parsed.contents) > 0, "Response must contain at least one content item"
    content = parsed.contents[0]
    assert content.uri == uri, "Content URI must match requested URI"
    assert isinstance(content.mimeType, str), "Content must have MIME type"
    assert (
        content.text is not None or content.blob is not None
    ), "Content must have text or blob"


@pytest.mark.mcp_requirement(
    feature="resources/read", level="MUST", req_id="RESOURCES-READ-2"
)
def test_resources_read_mime_type_matches(client):
    """Test that MIME type in read response matches listing."""
    # Get list of resources with MIME types
    resources = client.send("resources/list")
    resources_with_mime = [r for r in resources["resources"] if "mimeType" in r]
    if not resources_with_mime:
        pytest.skip("No resources with MIME type available")

    # Try to read a resource with known MIME type
    resource = resources_with_mime[0]
    result = client.send("resources/read", {"uri": resource["uri"]})
    parsed = ResourcesReadResult(**result)

    # Verify MIME type matches
    assert (
        parsed.contents[0].mimeType == resource["mimeType"]
    ), "MIME type must match listing"


@pytest.mark.mcp_requirement(
    feature="resources/read", level="MUST", req_id="RESOURCES-READ-3"
)
def test_resources_read_error_cases(client):
    """Test error handling for resources/read."""
    # Test with unknown URI
    with pytest.raises(JSONRPCError) as exc_info:
        client.send("resources/read", {"uri": "unknown://resource"})
    assert exc_info.value.code == -32002, "Should return resource not found error"

    # Test with missing URI parameter
    with pytest.raises(JSONRPCError) as exc_info:
        client.send("resources/read", {})
    assert exc_info.value.code == -32602, "Should return invalid params error"

    # Test with invalid URI type
    with pytest.raises(JSONRPCError) as exc_info:
        client.send("resources/read", {"uri": 123})
    assert exc_info.value.code == -32602, "Should return invalid params error"
