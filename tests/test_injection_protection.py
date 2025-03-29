import pytest


@pytest.mark.mcp_requirement(feature="security/sanitization", level="SHOULD")
def test_tools_call_does_not_echo_html(client, spec_version):
    """Test that tool responses do not include unsanitized HTML/script content."""
    params = {"name": "echo", "arguments": {"text": "<script>alert('XSS')</script>"}}
    response = client.send("tools/call", params)

    # Test that the response doesn't contain script tags directly
    assert "<script>" not in response.get("result", {}).get("output", "")
    # Either the tags should be escaped or removed
    assert "&lt;script&gt;" in response.get("result", {}).get(
        "output", ""
    ) or "script" not in response.get("result", {}).get("output", "")


@pytest.mark.mcp_requirement(feature="security/sanitization", level="SHOULD")
def test_tools_call_sanitizes_dangerous_attributes(client, spec_version):
    """Test that tool responses don't include dangerous HTML attributes."""
    params = {
        "name": "echo",
        "arguments": {"text": '<img src="x" onerror="alert(\'XSS\')">'},
    }
    response = client.send("tools/call", params)

    # Test that dangerous attributes are either removed or escaped
    assert "onerror=" not in response.get("result", {}).get("output", "")


@pytest.mark.mcp_requirement(feature="security/sanitization", level="SHOULD")
def test_prompts_get_rejects_script_injection(client, spec_version):
    """Test that prompts/get sanitizes or rejects script injection attempts."""
    params = {
        "name": "test_prompt",
        "arguments": {"arg1": '<img src="x" onerror="alert(\'XSS\')">'},
    }
    response = client.send("prompts/get", params)

    # Check that response doesn't contain dangerous HTML
    assert "onerror=" not in response.get("result", {}).get("content", "")


@pytest.mark.mcp_requirement(feature="security/sanitization", level="SHOULD")
def test_prompts_get_sanitizes_sql_injection(client, spec_version):
    """Test that prompts/get sanitizes or rejects SQL injection attempts."""
    params = {"name": "test_prompt", "arguments": {"arg1": "1' OR '1'='1"}}
    response = client.send("prompts/get", params)

    # Response should not contain SQL error messages
    assert "sql" not in response.get("result", {}).get("content", "").lower()
    assert "syntax error" not in response.get("result", {}).get("content", "").lower()
    assert "database" not in response.get("result", {}).get("content", "").lower()


@pytest.mark.mcp_requirement(feature="security/sanitization", level="SHOULD")
def test_tools_call_handles_unicode_safely(client, spec_version):
    """Test that tools/call safely processes Unicode characters."""
    params = {
        "name": "echo",
        "arguments": {"text": "Emoji 😀 and Unicode ⚠️ characters"},
    }
    response = client.send("tools/call", params)

    # Should be able to handle emoji without errors
    assert response.get("error") is None
    assert "😀" in response.get("result", {}).get("output", "")
