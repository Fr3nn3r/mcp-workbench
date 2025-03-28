"""Metadata for MCP specification requirements."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MCPRequirement:
    """Represents a single MCP specification requirement."""

    feature: str
    level: str  # MUST or SHOULD
    description: str
    id: Optional[str] = None


# Define all known MCP requirements
MCP_REQUIREMENTS = {
    "prompts/list": [
        MCPRequirement(
            feature="prompts/list",
            level="MUST",
            description="Server MUST return a list of available prompts",
            id="PROMPTS-LIST-1",
        ),
        MCPRequirement(
            feature="prompts/list",
            level="MUST",
            description="Each prompt MUST have a name field",
            id="PROMPTS-LIST-2",
        ),
        MCPRequirement(
            feature="prompts/list",
            level="SHOULD",
            description="Server SHOULD support pagination",
            id="PROMPTS-LIST-3",
        ),
    ],
    "prompts/get": [
        MCPRequirement(
            feature="prompts/get",
            level="MUST",
            description="Server MUST validate prompt name exists",
            id="PROMPTS-GET-1",
        ),
        MCPRequirement(
            feature="prompts/get",
            level="MUST",
            description="Server MUST validate required arguments",
            id="PROMPTS-GET-2",
        ),
        MCPRequirement(
            feature="prompts/get",
            level="MUST",
            description="Server MUST return valid message structure",
            id="PROMPTS-GET-3",
        ),
    ],
    "prompts/list_changed": [
        MCPRequirement(
            feature="prompts/list_changed",
            level="SHOULD",
            description="Server SHOULD declare listChanged capability",
            id="PROMPTS-LIST-CHANGED-1",
        ),
        MCPRequirement(
            feature="prompts/list_changed",
            level="SHOULD",
            description="Server SHOULD emit notification when list changes",
            id="PROMPTS-LIST-CHANGED-2",
        ),
    ],
}
