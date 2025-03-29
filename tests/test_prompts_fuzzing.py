import pytest


@pytest.mark.mcp_requirement(feature="prompts/get", level="SHOULD")
def test_prompts_get_argument_fuzzing(client, spec_version):
    """Test that prompts/get handles malformed arguments safely."""
    # Get available prompts
    prompts = client.send("prompts/list")["result"]["prompts"]
    prompt = next((p for p in prompts if p.get("arguments")), None)
    if not prompt:
        pytest.skip("No prompts with arguments")

    arg_name = prompt["arguments"][0]["name"]
    fuzz_cases = [
        "",  # empty string
        123,  # wrong type
        "💥🔥",  # unicode
        "'; DROP TABLE users; --",  # injection
        None,  # null (if accepted in JSON)
    ]

    for case in fuzz_cases:
        args = {arg_name: case}
        try:
            result = client.send(
                "prompts/get", {"name": prompt["name"], "arguments": args}
            )
            # If successful, response should still be valid
            assert "result" in result
            print(f"Server accepted fuzzing case: {case}")
        except Exception as e:
            error_msg = str(e).lower()
            assert "-32602" in error_msg or "invalid" in error_msg
            print(f"Server rejected fuzzing case: {case} with error: {error_msg}")


@pytest.mark.mcp_requirement(feature="prompts/get", level="SHOULD")
def test_prompts_get_extra_arguments(client, spec_version):
    """Test that prompts/get safely handles extra unknown arguments."""
    # Get available prompts
    prompts = client.send("prompts/list")["result"]["prompts"]
    if not prompts:
        pytest.skip("No prompts available")

    prompt = prompts[0]

    # Prepare normal arguments first
    args = {}
    if prompt.get("arguments"):
        for arg in prompt["arguments"]:
            if arg["required"]:
                args[arg["name"]] = "example value"

    # Add extra unknown arguments
    args["extra_unknown_arg"] = "should be ignored"
    args["another_extra"] = 12345

    # Call with extra arguments
    try:
        result = client.send("prompts/get", {"name": prompt["name"], "arguments": args})
        # If successful, response should still be valid
        assert "result" in result
        assert "messages" in result["result"]
        print("Server safely ignored extra arguments")
    except Exception as e:
        error_msg = str(e).lower()
        assert "-32602" in error_msg or "invalid" in error_msg
        print(f"Server rejected extra arguments with error: {error_msg}")


@pytest.mark.mcp_requirement(feature="prompts/get", level="SHOULD")
def test_prompts_get_wrong_argument_types(client, spec_version):
    """Test that prompts/get properly validates argument types."""
    # Get available prompts
    prompts = client.send("prompts/list")["result"]["prompts"]
    prompt = next((p for p in prompts if p.get("arguments")), None)
    if not prompt:
        pytest.skip("No prompts with arguments")

    wrong_type_values = [
        123,  # integer instead of string
        True,  # boolean instead of string
        {"nested": "obj"},  # object instead of simple value
        [1, 2, 3],  # array instead of simple value
    ]

    for val in wrong_type_values:
        arg_name = prompt["arguments"][0]["name"]
        args = {arg_name: val}

        try:
            result = client.send(
                "prompts/get", {"name": prompt["name"], "arguments": args}
            )
            # If the server accepts the value, it should still return a valid response
            assert "result" in result
            print(f"Server accepted wrong type: {val}")
        except Exception as e:
            error_msg = str(e).lower()
            assert "-32602" in error_msg or "invalid" in error_msg
            print(f"Server rejected wrong type: {val} with error: {error_msg}")
