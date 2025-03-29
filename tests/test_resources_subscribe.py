import pytest


@pytest.mark.mcp_requirement(feature="resources/subscribe", level="SHOULD")
def test_resources_subscribe_declared(client, spec_version):
    """Test that resources/subscribe capability is declared and functional."""
    # Check if the server declares the resources.subscribe capability
    caps = client.get_capabilities()
    if not caps.get("resources", {}).get("subscribe"):
        pytest.skip("Server does not declare resources.subscribe capability")

    # Get a resource to subscribe to
    resources = client.send("resources/list")["result"]["resources"]
    if not resources:
        pytest.skip("No resources available to subscribe to")

    # Use the first resource for testing
    uri = resources[0]["uri"]

    try:
        # Attempt to subscribe to the resource
        # Note: In a real implementation, we would need to handle the subscription
        # and listen for updates. For this test, we just verify the request doesn't fail.
        response = client.send("resources/subscribe", {"uri": uri})

        # There's no specific assertion here; we're just confirming the request doesn't raise an exception
        print(f"✅ Successfully subscribed to resource: {uri}")
    except Exception as e:
        # If subscribe is declared but not implemented, we'll get here
        pytest.fail(f"resources/subscribe failed despite being declared: {str(e)}")
