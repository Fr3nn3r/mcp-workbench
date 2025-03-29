from setuptools import setup

# This file is only needed to register the pytest plugin
setup(
    name="mcp-workbench",
    entry_points={
        "pytest11": ["mcp_mock_server = mcp.pytest_plugin"],
    },
)
