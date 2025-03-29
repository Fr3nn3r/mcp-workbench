import pytest


@pytest.mark.mcp_requirement(feature="resources/list", level="MUST")
def test_resources_list_responds(client, spec_version):
    """Test that resources/list returns a valid response."""
    response = client.send("resources/list")
    resources = response["result"]["resources"]
    assert isinstance(resources, list)


@pytest.mark.mcp_requirement(feature="resources/read", level="MUST")
def test_resources_read_returns_content(client, spec_version):
    """Test that resources/read returns content for a resource."""
    resources = client.send("resources/list")["result"]["resources"]
    if not resources:
        pytest.skip("No resources to read")
    uri = resources[0]["uri"]

    response = client.send("resources/read", {"uri": uri})
    contents = response["result"]["contents"]
    assert isinstance(contents, list)
    assert contents[0]["uri"] == uri
    assert "text" in contents[0] or "blob" in contents[0]


@pytest.mark.mcp_requirement(feature="resources/templates/list", level="MUST")
def test_resources_templates_list(client, spec_version):
    """Test that resources/templates/list returns a valid response."""
    response = client.send("resources/templates/list")
    templates = response["result"]["resourceTemplates"]
    assert isinstance(templates, list)
    for tmpl in templates:
        assert "uriTemplate" in tmpl
        assert "name" in tmpl
        assert "mimeType" in tmpl


@pytest.mark.mcp_requirement(feature="resources/list_changed", level="SHOULD")
def test_resources_list_changed_supported(client, spec_version):
    """Test that resources/list_changed is supported if declared."""
    caps = client.get_capabilities()
    if not caps.get("resources", {}).get("listChanged"):
        pytest.skip("Server does not declare resources.listChanged capability")
    # This test only verifies the capability is declared
    # A more thorough test would verify notification emission


@pytest.mark.mcp_requirement(feature="resources/subscribe", level="SHOULD")
def test_resources_subscribe_supported(client, spec_version):
    """Test that resources/subscribe is supported if declared."""
    caps = client.get_capabilities()
    if not caps.get("resources", {}).get("subscribe"):
        pytest.skip("Server does not declare resources.subscribe capability")
    # This test only verifies the capability is declared
    # A more thorough test would implement subscription handling
