"""MCP Test Runner with version awareness.

This module provides a command-line interface for running MCP specification tests
with support for different versions of the specification.
"""

import argparse
import os
from pathlib import Path
from typing import List, Dict
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VersionManager:
    """Manages MCP specification versions and their requirements."""

    def __init__(self, specs_dir: str = "specs"):
        """Initialize the version manager."""
        self.specs_dir = Path(specs_dir)
        self._supported_versions = self._get_supported_versions()
        self.current_version = None
        self.requirements = {}

    def _get_supported_versions(self) -> List[str]:
        """Get list of supported versions from specs directory."""
        if not self.specs_dir.exists():
            logger.error(f"Specs directory {self.specs_dir} not found")
            return []
        return [d.name for d in self.specs_dir.iterdir() if d.is_dir()]

    def validate_version(self, version: str) -> bool:
        """Validate if a version is supported."""
        if version not in self._supported_versions:
            logger.error(f"Unsupported version: {version}")
            logger.info(f"Supported versions: {', '.join(self._supported_versions)}")
            return False
        return True

    def load_requirements(self, version: str) -> Dict[str, dict]:
        """Load all requirements files for a given version."""
        if not self.validate_version(version):
            raise ValueError(
                f"Cannot load requirements for unsupported version: {version}"
            )

        self.current_version = version
        version_path = self.specs_dir / version
        requirement_files = [
            "prompts_requirements.txt",
            "resources_requirements.txt",
            "tools_requirements.txt",
            "utilities_requirements.txt",
        ]

        requirements = {}
        for req_file in requirement_files:
            file_path = version_path / req_file
            if file_path.exists():
                category = req_file.replace("_requirements.txt", "")
                with open(file_path, "r", encoding="utf-8") as f:
                    requirements[category] = f.read()
                logger.info(f"Loaded requirements from {req_file}")
            else:
                logger.warning(f"Requirements file not found: {req_file}")

        self.requirements = requirements
        return requirements


def main():
    """Main entry point for the MCP test runner."""
    parser = argparse.ArgumentParser(description="MCP Test Runner")
    parser.add_argument(
        "--spec-version",
        required=True,
        help="MCP specification version (e.g. 2024-11-05)",
    )

    args = parser.parse_args()

    # Initialize version manager
    version_manager = VersionManager()

    try:
        # Validate version and load requirements
        if not version_manager.validate_version(args.spec_version):
            sys.exit(1)

        requirements = version_manager.load_requirements(args.spec_version)
        logger.info(f"Successfully loaded requirements for version {args.spec_version}")

        # TODO: Add test discovery and execution logic here

    except Exception as e:
        logger.error(f"Error running tests: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
