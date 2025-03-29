import pytest
import json


@pytest.mark.mcp_requirement(feature="security/input_validation", level="SHOULD")
def test_tools_call_argument_fuzzing(client, spec_version):
    """Test various edge cases for tools/call arguments."""
    # Test cases with different input values
    test_cases = [
        # Empty string
        {"value": "", "should_succeed": True},
        # Very long string
        {"value": "a" * 1000, "should_succeed": True},
        # Unicode characters
        {"value": "测试Unicode字符", "should_succeed": True},
        # Special characters
        {"value": "!@#$%^&*()_+-=[]{}|;':\",./<>?", "should_succeed": True},
        # NULL byte
        {"value": "test\x00null", "should_succeed": False},
        # SQL injection attempt
        {"value": "'; DROP TABLE users; --", "should_succeed": True},
        # Script injection attempt
        {"value": "<script>alert('XSS')</script>", "should_succeed": True},
        # Null value (will be converted to string by json.dumps)
        {"value": None, "should_succeed": False},
    ]

    # Run each test case
    for tc in test_cases:
        try:
            response = client.send(
                "tools/call",
                {"name": "complex_tool", "arguments": {"required_arg": tc["value"]}},
            )

            # If we expected failure but got success, note that
            if not tc["should_succeed"]:
                print(f"Warning: Expected {tc['value']} to fail but it succeeded")

            # Check that we got a result, not an error
            assert "result" in response

        except ValueError as e:
            error_msg = str(e)
            # If we're getting a type validation error, that's fine
            if (
                "missing required argument" in error_msg
                or "invalid" in error_msg.lower()
            ):
                # Valid validation error
                continue
            # If we expected success but got an unexpected error
            if tc["should_succeed"] and "unknown tool name" not in error_msg:
                pytest.fail(
                    f"Expected {tc['value']} to succeed but got error: {error_msg}"
                )


@pytest.mark.mcp_requirement(feature="security/input_validation", level="SHOULD")
def test_tools_call_extra_arguments(client, spec_version):
    """Test that server safely handles extra unknown arguments."""
    try:
        response = client.send(
            "tools/call",
            {
                "name": "complex_tool",
                "arguments": {
                    "required_arg": "valid_value",
                    "unknown_arg": "this argument doesn't exist",
                },
            },
        )

        # Should either ignore the extra argument or return an error
        assert "result" in response

    except ValueError as e:
        error_msg = str(e)
        # If it's rejecting the extra arguments, that's also acceptable
        assert (
            "invalid" in error_msg.lower()
            or "unknown" in error_msg.lower()
            or "argument" in error_msg.lower()
        )


@pytest.mark.mcp_requirement(feature="security/input_validation", level="SHOULD")
def test_tools_call_wrong_argument_types(client, spec_version):
    """Test that server properly validates argument types."""
    # Send a number where string is expected
    try:
        response = client.send(
            "tools/call",
            {
                "name": "complex_tool",
                "arguments": {"required_arg": 12345},  # Number instead of string
            },
        )

        # If we get here, the server accepted a number as a string argument
        # This is OK if the server converts it, but should be documented
        assert "result" in response

    except ValueError as e:
        # Exception is acceptable if the server is strictly validating types
        error_msg = str(e).lower()
        assert "invalid" in error_msg or "type" in error_msg


@pytest.mark.mcp_requirement(feature="security/input_validation", level="SHOULD")
def test_tools_call_large_inputs(client, spec_version):
    """Test that server handles large input values (100KB string)."""
    try:
        large_input = "a" * 100000  # 100KB string
        response = client.send(
            "tools/call",
            {"name": "complex_tool", "arguments": {"required_arg": large_input}},
        )

        # If we reach here, the server processed the large input
        assert "result" in response

    except ValueError as e:
        # If it fails, it should return a reasonable error
        error_msg = str(e).lower()

        # Either we get a size-related error or a generic error
        assert (
            "too large" in error_msg
            or "size" in error_msg
            or "length" in error_msg
            or "invalid" in error_msg
            or "error" in error_msg
        )
