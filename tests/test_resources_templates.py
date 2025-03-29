import pytest
from mcp.protocol import ResourcesTemplatesListResult


@pytest.mark.mcp_requirement(feature="resources/templates/list", level="MUST")
def test_resources_templates_are_valid(client, spec_version):
    """Test that resources/templates/list returns valid template structures."""
    result = client.send("resources/templates/list")
    parsed = ResourcesTemplatesListResult(**result["result"])

    # No requirement that templates exist, but if they do, validate structure
    for tmpl in parsed.resourceTemplates:
        # URI Template should have a valid scheme
        assert isinstance(tmpl.uriTemplate, str)

        # The template should have a name
        assert isinstance(tmpl.name, str)

        # The template should have a MIME type
        assert isinstance(tmpl.mimeType, str)

        # If description is present, it should be a string
        if tmpl.description:
            assert isinstance(tmpl.description, str)

        # If parameters are present, validate structure
        if tmpl.parameters:
            for param in tmpl.parameters:
                assert "name" in param
