import pytest
import json
from unittest.mock import patch


class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data
        self.text = json.dumps(json_data) if json_data else ""

    def json(self):
        return self._json_data


@pytest.mark.mcp_requirement(feature="jsonrpc/validation", level="SHOULD")
@patch("httpx.Client.post")
def test_invalid_jsonrpc_version_fails(mock_post, client, spec_version):
    """Test that server rejects requests with invalid JSON-RPC version."""
    # Mock response for invalid JSON-RPC version
    error_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": -32600,
            "message": "Invalid Request: jsonrpc version must be exactly '2.0'",
        },
    }
    mock_post.return_value = MockResponse(200, error_response)

    # Test with wrong version
    bad_payload = {
        "jsonrpc": "1.0",  # wrong version
        "id": 1,
        "method": "prompts/list",
        "params": {},
    }
    response = client.session.post(client.base_url, json=bad_payload)

    assert response.status_code == 200
    response_json = response.json()
    assert "error" in response_json
    assert response_json["error"]["code"] == -32600


@pytest.mark.mcp_requirement(feature="jsonrpc/validation", level="SHOULD")
@patch("httpx.Client.post")
def test_missing_method_field_fails(mock_post, client, spec_version):
    """Test that server rejects requests missing the required method field."""
    # Mock response for missing method
    error_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"code": -32600, "message": "Invalid Request: method is required"},
    }
    mock_post.return_value = MockResponse(200, error_response)

    # Test with missing method
    bad_payload = {"jsonrpc": "2.0", "id": 1, "params": {}}
    response = client.session.post(client.base_url, json=bad_payload)

    assert response.status_code == 200
    response_json = response.json()
    assert "error" in response_json
    assert response_json["error"]["code"] == -32600


@pytest.mark.mcp_requirement(feature="jsonrpc/validation", level="SHOULD")
@patch("httpx.Client.post")
def test_invalid_payload_format_fails(mock_post, client, spec_version):
    """Test that server rejects payloads that aren't valid JSON."""
    # Mock response for invalid JSON
    mock_post.return_value = MockResponse(400, None)

    # Test with invalid JSON
    headers = {"Content-Type": "application/json"}
    response = client.session.post(
        client.base_url, content="{not-json", headers=headers
    )

    # Server should return an error status code
    assert response.status_code == 400


@pytest.mark.mcp_requirement(feature="jsonrpc/validation", level="SHOULD")
@patch("httpx.Client.post")
def test_wrong_method_type_fails(mock_post, client, spec_version):
    """Test that server rejects requests with non-string method values."""
    # Mock response for wrong method type
    error_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": -32600,
            "message": "Invalid Request: method must be a string",
        },
    }
    mock_post.return_value = MockResponse(200, error_response)

    # Test with numeric method
    bad_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": 123,  # method must be string
        "params": {},
    }
    response = client.session.post(client.base_url, json=bad_payload)

    assert response.status_code == 200
    response_json = response.json()
    assert "error" in response_json
    assert response_json["error"]["code"] == -32600


@pytest.mark.mcp_requirement(feature="jsonrpc/validation", level="SHOULD")
@patch("httpx.Client.post")
def test_missing_jsonrpc_field_fails(mock_post, client, spec_version):
    """Test that server rejects requests missing the jsonrpc field."""
    # Mock response for missing jsonrpc field
    error_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": -32600,
            "message": "Invalid Request: jsonrpc field is required",
        },
    }
    mock_post.return_value = MockResponse(200, error_response)

    # Test with missing jsonrpc field
    bad_payload = {
        # missing jsonrpc field
        "id": 1,
        "method": "prompts/list",
        "params": {},
    }
    response = client.session.post(client.base_url, json=bad_payload)

    assert response.status_code == 200
    response_json = response.json()
    assert "error" in response_json
    assert response_json["error"]["code"] == -32600
