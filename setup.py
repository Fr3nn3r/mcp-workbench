"""Setup configuration for mcp-workbench."""

from setuptools import setup, find_namespace_packages

setup(
    name="mcp-workbench",
    packages=find_namespace_packages(include=["mcp*", "mock_server*"]),
)
