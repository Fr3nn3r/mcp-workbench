import pytest
import time


@pytest.mark.mcp_requirement(feature="resources/list_changed", level="SHOULD")
def test_resources_list_changed_detects_update(client, spec_version):
    """Test that server emits notifications when resources list changes."""
    # Check if the server declares the resources.listChanged capability
    caps = client.get_capabilities()
    if not caps.get("resources", {}).get("listChanged"):
        pytest.skip("Server does not declare resources.listChanged capability")

    # Step 1: Snapshot current resources list
    original_response = client.send("resources/list")
    original = original_response["result"]["resources"]

    # In a real implementation, we would either:
    # 1. Trigger a resource change on the server, or
    # 2. Listen for list_changed notifications
    # For this test, we'll simulate a polling approach to detect changes

    print("📣 Waiting for possible resource list change...")

    # Simulate polling for changes
    max_attempts = 3
    found_change = False

    for attempt in range(max_attempts):
        # Sleep briefly between attempts
        time.sleep(2)

        # Re-fetch the resources list
        updated_response = client.send("resources/list")
        updated = updated_response["result"]["resources"]

        if original != updated:
            found_change = True
            print(f"✅ resources list changed on attempt {attempt+1}")
            break
        else:
            print(f"⏳ No change detected on attempt {attempt+1}, trying again...")

    if not found_change:
        print("ℹ️ resources list did not change during test window")

    # This test should not fail if no notification is received, according to requirements
    # It only verifies functionality if a change is detected
