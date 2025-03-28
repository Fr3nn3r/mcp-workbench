"""Test cases for prompts list change detection."""

import time
import pytest
from mcp.client import JSONRPCError


@pytest.mark.mcp_requirement(
    feature="prompts/list_changed", level="SHOULD", req_id="PROMPTS-LIST-CHANGED-1"
)
def test_prompts_list_changed_capability(client):
    """Test that server declares prompts.listChanged capability correctly."""
    capabilities = client.send("capabilities/get")
    prompts_cap = capabilities.get("prompts", {})

    if not prompts_cap.get("listChanged", False):
        pytest.skip("Server does not declare prompts.listChanged = true")

    # If we get here, the server declares listChanged support
    assert prompts_cap["listChanged"] is True


@pytest.mark.mcp_requirement(
    feature="prompts/list_changed", level="SHOULD", req_id="PROMPTS-LIST-CHANGED-2"
)
def test_prompts_list_changed_detects_change(client):
    """Test that changes in the prompts list can be detected.

    This test:
    1. Checks if server supports listChanged
    2. Takes initial snapshot of prompts
    3. Waits for potential changes
    4. Checks if list has changed
    """
    # Check capability first
    capabilities = client.send("capabilities/get")
    if not capabilities.get("prompts", {}).get("listChanged"):
        pytest.skip("listChanged capability not declared")

    # Get initial prompt list
    initial_list = client.send("prompts/list")
    initial_prompts = initial_list.get("prompts", [])

    # Wait for potential changes (reduced time for testing)
    print("Waiting for possible prompt list change (5s)...")
    time.sleep(5)  # Reduced from 10s to 5s for faster testing

    # Get updated list
    updated_list = client.send("prompts/list")
    updated_prompts = updated_list.get("prompts", [])

    # Compare lists - we don't fail if they're the same since changes are optional
    if initial_prompts != updated_prompts:
        print("✅ prompts list changed (server likely emitted notification)")
    else:
        print("ℹ️ prompts list did not change")

    # Basic validation of both lists
    assert isinstance(initial_prompts, list), "Initial prompts should be a list"
    assert isinstance(updated_prompts, list), "Updated prompts should be a list"

    # Validate structure of prompts in both lists
    for prompts in [initial_prompts, updated_prompts]:
        for prompt in prompts:
            assert isinstance(prompt, dict), "Each prompt should be a dictionary"
            assert "name" in prompt, "Each prompt should have a name"
            assert isinstance(prompt["name"], str), "Prompt name should be a string"
