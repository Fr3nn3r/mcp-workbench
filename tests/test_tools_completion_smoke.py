import pytest


# TOOLS


@pytest.mark.mcp_requirement(feature="tools/list", level="MUST")
def test_tools_list_responds(client, spec_version):
    """Test that tools/list returns a valid response."""
    response = client.send("tools/list")
    tools = response["result"]["tools"]
    assert isinstance(tools, list)


@pytest.mark.mcp_requirement(feature="tools/call", level="MUST")
def test_tools_call_accepts_valid_input(client, spec_version):
    """Test that tools/call accepts valid input and returns appropriate response."""
    tools = client.send("tools/list")["result"]["tools"]
    if not tools:
        pytest.skip("No tools available")

    tool = tools[0]
    schema = tool.get("inputSchema", {})
    args = {}

    # Prepare arguments based on the tool schema
    for name in schema.get("required", []):
        args[name] = "example input"

    # Call the tool
    result = client.send("tools/call", {"name": tool["name"], "arguments": args})

    # Validate the response structure
    assert "content" in result["result"]
    for item in result["result"]["content"]:
        assert item["type"] in ("text", "image", "resource")


@pytest.mark.mcp_requirement(feature="tools/list_changed", level="SHOULD")
def test_tools_list_changed_supported(client, spec_version):
    """Test that server declares tools/list_changed capability if supported."""
    caps = client.get_capabilities()
    if not caps.get("tools", {}).get("listChanged"):
        pytest.skip("Server does not declare tools.listChanged capability")

    # In a real implementation, we would test this by:
    # 1. Setting up a notification listener
    # 2. Triggering a change to the tools list
    # 3. Verifying a notification is received

    print("✅ Server declares tools.listChanged capability")


# COMPLETION


@pytest.mark.mcp_requirement(feature="completion/complete", level="MUST")
def test_prompt_argument_completion_supported(client, spec_version):
    """Test that completion/complete supports prompt argument completion."""
    prompts = client.send("prompts/list")["result"]["prompts"]
    prompt = next((p for p in prompts if p.get("arguments")), None)
    if not prompt:
        pytest.skip("No prompt with arguments")

    arg = prompt["arguments"][0]["name"]
    result = client.send(
        "completion/complete",
        {
            "ref": {"type": "ref/prompt", "name": prompt["name"]},
            "argument": {"name": arg, "value": "ex"},
        },
    )

    # Validate the completion response
    completion = result["result"]["completion"]
    assert isinstance(completion["values"], list)
    assert "hasMore" in completion


@pytest.mark.mcp_requirement(feature="completion/complete", level="SHOULD")
def test_resource_uri_completion_supported(client, spec_version):
    """Test that completion/complete supports resource URI completion."""
    templates = client.send("resources/templates/list")["result"]["resourceTemplates"]
    if not templates:
        pytest.skip("No resource templates available")

    uri = templates[0]["uriTemplate"]
    result = client.send(
        "completion/complete",
        {
            "ref": {"type": "ref/resource", "uri": uri},
            "argument": {"name": "path", "value": "src/"},
        },
    )

    # Validate the completion response
    completion = result["result"]["completion"]
    assert isinstance(completion["values"], list)
