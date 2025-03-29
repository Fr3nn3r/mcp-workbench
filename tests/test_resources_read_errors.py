import pytest


@pytest.mark.mcp_requirement(feature="resources/read", level="SHOULD")
def test_resources_read_nonexistent_uri_fails(client, spec_version):
    """Test that resources/read fails with appropriate error when URI doesn't exist."""
    with pytest.raises(Exception) as exc_info:
        client.send("resources/read", {"uri": "file:///nonexistent/xyz.fake"})

    # Check that the error message contains either the error code or a descriptive message
    error_msg = str(exc_info.value)
    assert any(err in error_msg for err in ["-32002", "not found", "NotFound"])


@pytest.mark.mcp_requirement(feature="resources/read", level="MUST")
def test_resources_read_missing_uri_param_fails(client, spec_version):
    """Test that resources/read fails when required uri parameter is missing."""
    with pytest.raises(Exception) as exc_info:
        client.send("resources/read", {})

    # Check that the error message contains either the error code or a descriptive message
    error_msg = str(exc_info.value)
    assert any(err in error_msg for err in ["-32602", "Invalid params", "missing uri"])
