"""Test cases for resource subscriptions and notifications."""

import time
import pytest
from mcp.client import JSONRPCError


@pytest.mark.mcp_requirement(
    feature="resources/subscribe", level="SHOULD", req_id="RESOURCES-SUBSCRIBE-1"
)
def test_resources_subscribe_capability(client):
    """Test that server declares resources.subscribe capability correctly."""
    capabilities = client.send("capabilities/get")
    resources_cap = capabilities.get("resources", {})

    if not resources_cap.get("subscribe", False):
        pytest.skip("Server does not declare resources.subscribe = true")

    # If we get here, the server declares subscribe support
    assert resources_cap["subscribe"] is True


@pytest.mark.mcp_requirement(
    feature="resources/subscribe", level="SHOULD", req_id="RESOURCES-SUBSCRIBE-2"
)
def test_resources_subscribe_lifecycle(client):
    """Test the subscription lifecycle for a resource.

    This test:
    1. Checks if server supports subscriptions
    2. Gets a resource to subscribe to
    3. Subscribes to the resource
    4. Waits for potential changes
    5. Unsubscribes from the resource
    """
    # Check capability first
    capabilities = client.send("capabilities/get")
    if not capabilities.get("resources", {}).get("subscribe"):
        pytest.skip("subscribe capability not declared")

    # Get a resource to subscribe to
    resources = client.send("resources/list")
    if not resources["resources"]:
        pytest.skip("No resources available")

    uri = resources["resources"][0]["uri"]

    # Subscribe to the resource
    try:
        result = client.send("resources/subscribe", {"uri": uri})
        assert (
            "subscriptionId" in result
        ), "Subscribe response must include subscriptionId"
        subscription_id = result["subscriptionId"]

        # Wait for potential notifications
        print(f"Waiting for possible resource updates (5s) for {uri}...")
        time.sleep(5)  # Reduced from 10s to 5s for faster testing

    finally:
        # Always try to unsubscribe if we got this far
        if subscription_id:
            client.send("resources/unsubscribe", {"subscriptionId": subscription_id})


@pytest.mark.mcp_requirement(
    feature="resources/subscribe", level="MUST", req_id="RESOURCES-SUBSCRIBE-3"
)
def test_resources_subscribe_error_cases(client):
    """Test error handling for resource subscriptions."""
    # Skip if subscriptions not supported
    capabilities = client.send("capabilities/get")
    if not capabilities.get("resources", {}).get("subscribe"):
        pytest.skip("subscribe capability not declared")

    # Test with unknown URI
    with pytest.raises(JSONRPCError) as exc_info:
        client.send("resources/subscribe", {"uri": "unknown://resource"})
    assert exc_info.value.code == -32002, "Should return resource not found error"

    # Test with missing URI
    with pytest.raises(JSONRPCError) as exc_info:
        client.send("resources/subscribe", {})
    assert exc_info.value.code == -32602, "Should return invalid params error"

    # Test unsubscribe with invalid subscription ID
    with pytest.raises(JSONRPCError) as exc_info:
        client.send("resources/unsubscribe", {"subscriptionId": "invalid_id"})
    assert exc_info.value.code == -32602, "Should return invalid params error"
