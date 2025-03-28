# MCP Workbench

A test runner for validating MCP (Model Control Protocol) implementations against specific versions of the specification.

## Features

- Version-aware test execution
- Dynamic loading of version-specific requirements
- Clear error reporting for unsupported versions
- Support for multiple requirement categories (prompts, resources, tools, utilities)

## Installation

```bash
pip install -e .
```

## Usage

Run tests for a specific MCP version:

```bash
python main.py --spec-version 2024-11-05
```

The runner will:
1. Validate the specified version against supported versions
2. Load the appropriate requirements for that version
3. Execute tests with the loaded requirements

## Supported Versions

The test runner automatically detects supported versions by scanning the `specs` directory. Each version should have its own directory containing requirement files:

- prompts_requirements.txt
- resources_requirements.txt
- tools_requirements.txt
- utilities_requirements.txt

## Error Handling

- If an unsupported version is specified, the runner will exit with a clear error message and list supported versions
- Missing requirement files are logged as warnings
- Other errors during test execution are clearly reported

## Development

Requirements:
- Python 3.8+
- Dependencies listed in pyproject.toml
