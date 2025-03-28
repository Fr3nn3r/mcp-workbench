#!/usr/bin/env python3
"""Test runner script for MCP compliance testing."""

import argparse
import logging
import sys
import pytest
from mcp.version_manager import VersionManager

# Default values
DEFAULT_SPEC_VERSION = "2024-11-05"
DEFAULT_SERVER_URL = "http://127.0.0.1:8000"


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="MCP Compliance Test Runner")
    parser.add_argument(
        "--spec-version",
        default=DEFAULT_SPEC_VERSION,
        help=f"MCP specification version (default: {DEFAULT_SPEC_VERSION})",
    )
    parser.add_argument(
        "--server-url",
        default=DEFAULT_SERVER_URL,
        help=f"Base URL of the MCP server to test (default: {DEFAULT_SERVER_URL})",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)
    logger = logging.getLogger(__name__)

    # Initialize version manager
    version_manager = VersionManager()

    # Validate spec version
    if not version_manager.validate_version(args.spec_version):
        sys.exit(1)

    # Load requirements for the specified version
    try:
        version_manager.load_requirements(args.spec_version)
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    # Run pytest with our arguments
    pytest_args = [
        "--server-url",
        args.server_url,
        "-v" if args.verbose else "",
        "tests",
    ]

    exit_code = pytest.main(list(filter(None, pytest_args)))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
