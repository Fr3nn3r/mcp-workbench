"""Test cases for resources/templates/list endpoint."""

import pytest
from mcp.client import JSONRPCError
from mcp.protocol.schema import ResourcesTemplatesListResult


@pytest.mark.mcp_requirement(
    feature="resources/templates", level="MUST", req_id="RESOURCES-TEMPLATES-1"
)
def test_resources_templates_list(client):
    """Test that resources/templates/list returns valid templates."""
    result = client.send("resources/templates/list")
    parsed = ResourcesTemplatesListResult(**result)

    # Validate each template
    for tmpl in parsed.resourceTemplates:
        assert isinstance(tmpl.uriTemplate, str), "Template URI must be a string"
        assert isinstance(tmpl.name, str), "Template name must be a string"
        assert isinstance(tmpl.mimeType, str), "Template MIME type must be a string"
        if tmpl.description:
            assert isinstance(
                tmpl.description, str
            ), "Template description must be a string"


@pytest.mark.mcp_requirement(
    feature="resources/templates", level="MUST", req_id="RESOURCES-TEMPLATES-2"
)
def test_resources_templates_uri_format(client):
    """Test that template URIs follow the correct format."""
    result = client.send("resources/templates/list")
    parsed = ResourcesTemplatesListResult(**result)

    for tmpl in parsed.resourceTemplates:
        # Check that URI template contains at least one parameter
        assert (
            "{" in tmpl.uriTemplate and "}" in tmpl.uriTemplate
        ), "URI template must contain at least one parameter"

        # Basic format validation (scheme://path)
        assert "://" in tmpl.uriTemplate, "URI template must include scheme"


@pytest.mark.mcp_requirement(
    feature="resources/templates", level="SHOULD", req_id="RESOURCES-TEMPLATES-3"
)
def test_resources_templates_mime_types(client):
    """Test that template MIME types are valid."""
    result = client.send("resources/templates/list")
    parsed = ResourcesTemplatesListResult(**result)

    for tmpl in parsed.resourceTemplates:
        # Basic MIME type format validation
        assert "/" in tmpl.mimeType, "MIME type must be in format type/subtype"
        type_part = tmpl.mimeType.split("/")[0]
        assert type_part in [
            "text",
            "image",
            "audio",
            "video",
            "application",
        ], f"Invalid MIME type main type: {type_part}"
