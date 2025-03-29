# MCP Workbench

A testing workbench for validating MCP (Model Control Protocol) implementations against specific versions of the specification.

## Features

- Version-aware test execution
- Dynamic loading of version-specific requirements
- Clear error reporting for unsupported versions
- Support for multiple requirement categories (prompts, resources, tools, utilities)
- Filtering by feature and requirement level
- JSON report generation

## Installation

```bash
# For development (editable install)
pip install -e .

# For regular use
pip install .
```

## CLI Usage

After installation, you can use the `mcp-check` command line tool:

```bash
# Basic usage
mcp-check --server-url http://localhost:8000

# Specify MCP version
mcp-check --server-url http://localhost:8000 --spec-version 2024-11-05

# Filter by features
mcp-check --server-url http://localhost:8000 --features prompts,tools

# Filter by requirement level (MUST, SHOULD)
mcp-check --server-url http://localhost:8000 --level MUST

# Generate JSON report
mcp-check --server-url http://localhost:8000 --json-report ./reports/custom-report.json

# Verbose output
mcp-check --server-url http://localhost:8000 --verbose
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--server-url` | URL of the MCP server to test | (Required) |
| `--spec-version` | MCP specification version | 2024-11-05 |
| `--features` | Comma-separated list of features to test | all |
| `--level` | Comma-separated list of requirement levels | MUST,SHOULD |
| `--json-report` | Path to save the JSON report | reports/summary.json |
| `--verbose` or `-v` | Show verbose output | False |

## Supported Versions

The test runner automatically detects supported versions by scanning the `specs` directory. Each version should have its own directory containing requirement files:

- prompts_requirements.txt
- resources_requirements.txt
- tools_requirements.txt
- utilities_requirements.txt

## Error Handling

- If an unsupported version is specified, the runner will exit with a clear error message and list supported versions
- Missing requirement files are logged as warnings
- Failed MUST-level requirements will cause a non-zero exit code

## CI Integration

MCP Workbench is designed to be used in CI/CD pipelines. It will:

- Return a non-zero exit code if any MUST-level requirements fail
- Generate a JSON report for further processing
- Provide a human-readable summary on the console

Example GitHub Actions workflow:

```yaml
name: MCP Compliance

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install
        run: |
          pip install -e .

      - name: Run MCP Check
        run: |
          mcp-check --server-url http://localhost:8000 --spec-version 2024-11-05
```

## Development

Requirements:
- Python 3.8+
- Dependencies listed in pyproject.toml

## Project Structure

```
mcp-workbench/
├── mcp/                  # protocol models, client, registry
│   ├── __init__.py
│   ├── cli.py            # CLI entry point
│   ├── client.py
│   ├── protocol.py
│   ├── spec_registry.py
├── tests/                # Test files
├── conftest.py           # fixtures + compliance logging
├── pyproject.toml        # packaging metadata
├── README.md
└── reports/              # Generated reports
    └── summary.json
```

## Using the Mock MCP Server

The workbench includes a mock MCP server that can be used for local testing and CI environments. This server implements the MCP protocol and responds to all standard methods with realistic responses.

### Run as a standalone server

To run the mock server as a standalone process:

```bash
# Set environment variable to use Flask
export FLASK_APP=mcp.mock_server
# Run server on port 8000
flask run --port=8000
```

### Use with pytest

For CI environments or automated testing, you can use the `--mock-server` flag with pytest:

```bash
# Run tests with the mock server
pytest --mock-server
```

This will start an in-process mock server on port 8000 and configure tests to use it automatically.

### Mock Server Features

The mock server supports:

- Basic MCP endpoints:
  - `prompts/list`, `prompts/get`
  - `tools/list`, `tools/call`
  - `resources/list`, `resources/read`, etc.
- Error simulation
- Rate limiting
- Access control with the admin_only_tool
- Proper JSON-RPC validation
- Custom admin endpoints to configure behavior

### Configuring Server Behavior

The server has an admin endpoint for configuring behavior during testing:

```bash
# Example: Configure server to simulate slow responses
curl -X POST http://localhost:8000/admin/config \
  -H "Content-Type: application/json" \
  -d '{"slow_response": true}'
```

Available configuration options:
- `simulate_errors`: Force certain endpoints to return errors
- `slow_response`: Add a delay to responses
- `force_invalid_json`: Return an invalid JSON response (useful for testing error handling)
