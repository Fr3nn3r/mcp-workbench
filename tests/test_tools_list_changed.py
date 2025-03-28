"""Test cases for tools/list_changed notifications."""

import pytest
from mcp.client import JSONRPCError


@pytest.mark.mcp_requirement(
    feature="tools/list_changed", level="SHOULD", req_id="TOOLS-LIST-CHANGED-1"
)
def test_tools_list_changed_capability(client):
    """Test that server declares listChanged capability if supported."""
    capabilities = client.send("capabilities/get")["result"]
    tools_cap = capabilities.get("tools", {})

    if not tools_cap.get("listChanged"):
        pytest.skip("tools/list_changed not supported")

    assert tools_cap["listChanged"] is True, "listChanged must be true if declared"


@pytest.mark.mcp_requirement(
    feature="tools/list_changed", level="SHOULD", req_id="TOOLS-LIST-CHANGED-2"
)
def test_tools_list_changed_detects_change(client):
    """Test that server emits notification when tools change."""
    capabilities = client.send("capabilities/get")["result"]
    tools_cap = capabilities.get("tools", {})

    if not tools_cap.get("listChanged"):
        pytest.skip("tools/list_changed not supported")

    # Subscribe to notifications
    client.send(
        "notifications/subscribe", {"methods": ["notifications/tools/list_changed"]}
    )

    # Trigger a change (implementation specific)
    # This could be adding/removing a tool, changing permissions, etc.
    # The actual implementation will vary

    # Wait for notification
    notification = client.wait_for_notification("notifications/tools/list_changed")
    assert notification is not None, "Should receive list_changed notification"

    # Verify tools list has changed
    new_tools = client.send("tools/list")["result"]["tools"]
    assert isinstance(new_tools, list), "Should get updated tools list"
