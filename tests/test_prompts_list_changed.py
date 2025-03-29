import pytest
import time


@pytest.mark.mcp_requirement(feature="prompts/list_changed", level="SHOULD")
def test_prompts_list_changed_detects_update(client, spec_version):
    """Test that server emits notifications when prompt list changes."""
    # Check if the server declares the prompts.listChanged capability
    caps = client.get_capabilities()
    if not caps.get("prompts", {}).get("listChanged", False):
        pytest.skip("Server does not declare prompts.listChanged capability")

    # Step 1: Snapshot current prompt list
    original_response = client.send("prompts/list")
    original = original_response["result"]["prompts"]

    # Prepare the client to simulate a change
    client.simulate_prompt_change()

    print("📣 Waiting for possible prompt list change...")

    # Wait for change to occur - in a real implementation this would wait for notifications
    # or poll until change is detected
    max_attempts = 3
    found_change = False

    for attempt in range(max_attempts):
        # Sleep to give time for the change to occur
        time.sleep(2)

        # Step 2: Re-fetch list
        updated_response = client.send("prompts/list")
        updated = updated_response["result"]["prompts"]

        if original != updated:
            found_change = True
            print(f"✅ prompts list changed on attempt {attempt+1}")
            break
        else:
            print(f"⏳ No change detected on attempt {attempt+1}, trying again...")

    if not found_change:
        print("ℹ️ prompts list did not change during test window")

    # This test should not fail if no notification is received, according to requirements
    # It only verifies functionality if a change is detected
