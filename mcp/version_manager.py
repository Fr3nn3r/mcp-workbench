"""Version management module for MCP test runner.

This module handles version validation and requirements loading for different MCP spec versions.
"""

import os
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VersionManager:
    """Manages MCP specification versions and their requirements."""

    def __init__(self, specs_dir: str = "specs"):
        """Initialize the version manager.

        Args:
            specs_dir: Directory containing the spec versions
        """
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
        """Validate if a version is supported.

        Args:
            version: Version string to validate (e.g. '2024-11-05')

        Returns:
            bool: True if version is supported, False otherwise
        """
        if version not in self._supported_versions:
            logger.error(f"Unsupported version: {version}")
            logger.info(f"Supported versions: {', '.join(self._supported_versions)}")
            return False
        return True

    def load_requirements(self, version: str) -> Dict[str, dict]:
        """Load all requirements files for a given version.

        Args:
            version: Version string (e.g. '2024-11-05')

        Returns:
            Dict containing requirements from all requirement files
        """
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

    def get_current_version(self) -> str:
        """Get the currently loaded version."""
        return self.current_version

    def get_current_requirements(self) -> Dict[str, dict]:
        """Get the currently loaded requirements."""
        return self.requirements
