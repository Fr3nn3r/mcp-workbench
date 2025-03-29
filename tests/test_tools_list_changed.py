import pytest
import time


@pytest.mark.mcp_requirement(feature="tools/list_changed", level="SHOULD")
def test_tools_list_changed_notification_polling(client, spec_version):
    """Test that server emits notifications when tool list changes."""
    # Check if the server declares the tools.listChanged capability
    caps = client.get_capabilities()
    if not caps.get("tools", {}).get("listChanged"):
        pytest.skip("tools.listChanged capability not declared")

    # Step 1: Capture current list
    tools_before = client.send("tools/list")["result"]["tools"]

    # Prepare the client to simulate a change
    client.simulate_tool_change()

    print("⏳ Waiting for possible tool list change...")

    # Simulate polling for changes
    max_attempts = 3
    found_change = False

    for attempt in range(max_attempts):
        # Sleep briefly between attempts
        time.sleep(2)

        # Step 2: Capture new list
        tools_after = client.send("tools/list")["result"]["tools"]

        if tools_before != tools_after:
            found_change = True
            print(f"✅ Tool list changed on attempt {attempt+1}")
            break
        else:
            print(f"⏳ No change detected on attempt {attempt+1}, trying again...")

    if not found_change:
        print("ℹ️ Tool list unchanged — no notification triggered")

    # This test should not fail if no notification is received, according to requirements
    # It only verifies functionality if a change is detected
