import pytest
from mcp.protocol import ResourcesReadResult


@pytest.mark.mcp_requirement(feature="resources/read", level="MUST")
def test_resources_read_returns_text_or_blob(client, spec_version):
    """Test that resources/read returns content in either text or blob format."""
    # Get list of available resources first
    resources = client.send("resources/list")["result"]["resources"]
    if not resources:
        pytest.skip("No resources available to read")

    # Use the first resource for testing
    uri = resources[0]["uri"]

    # Call resources/read
    response = client.send("resources/read", {"uri": uri})
    parsed = ResourcesReadResult(**response["result"])

    # Validate response structure
    assert len(parsed.contents) > 0

    content = parsed.contents[0]
    assert content.uri == uri
    assert isinstance(content.mimeType, str)

    # Must have either text or blob content
    assert content.text is not None or content.blob is not None

    if content.text is not None:
        assert isinstance(content.text, str)

    if content.blob is not None:
        assert isinstance(content.blob, str)
