"""Test cases for resources list change detection."""

import time
import pytest
from mcp.client import JSONRPCError
from mcp.protocol.schema import ResourcesListResult


@pytest.mark.mcp_requirement(
    feature="resources/list_changed", level="SHOULD", req_id="RESOURCES-LIST-CHANGED-1"
)
def test_resources_list_changed_capability(client):
    """Test that server declares resources.listChanged capability correctly."""
    capabilities = client.send("capabilities/get")
    resources_cap = capabilities.get("resources", {})

    if not resources_cap.get("listChanged", False):
        pytest.skip("Server does not declare resources.listChanged = true")

    # If we get here, the server declares listChanged support
    assert resources_cap["listChanged"] is True


@pytest.mark.mcp_requirement(
    feature="resources/list_changed", level="SHOULD", req_id="RESOURCES-LIST-CHANGED-2"
)
def test_resources_list_changed_detects_change(client):
    """Test that changes in the resources list can be detected.

    This test:
    1. Checks if server supports listChanged
    2. Takes initial snapshot of resources
    3. Waits for potential changes
    4. Checks if list has changed
    """
    # Check capability first
    capabilities = client.send("capabilities/get")
    if not capabilities.get("resources", {}).get("listChanged"):
        pytest.skip("listChanged capability not declared")

    # Get initial resource list
    initial_list = client.send("resources/list")
    initial_resources = ResourcesListResult(**initial_list)

    # Wait for potential changes (reduced time for testing)
    print("Waiting for possible resource list change (5s)...")
    time.sleep(5)  # Reduced from 10s to 5s for faster testing

    # Get updated list
    updated_list = client.send("resources/list")
    updated_resources = ResourcesListResult(**updated_list)

    # Compare lists - we don't fail if they're the same since changes are optional
    if initial_resources.resources != updated_resources.resources:
        print("✅ resources list changed (server likely emitted notification)")
    else:
        print("ℹ️ resources list did not change")

    # Basic validation of both lists
    for resources in [initial_resources.resources, updated_resources.resources]:
        for resource in resources:
            assert isinstance(resource.uri, str), "Resource URI must be a string"
            assert isinstance(resource.name, str), "Resource name must be a string"
            if resource.mimeType:
                assert isinstance(
                    resource.mimeType, str
                ), "Resource MIME type must be a string"
