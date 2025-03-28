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
    "resources/list": [
        MCPRequirement(
            feature="resources/list",
            level="MUST",
            description="Server MUST return a valid list of resources",
            id="RESOURCES-LIST-1",
        ),
        MCPRequirement(
            feature="resources/list",
            level="SHOULD",
            description="Server SHOULD support pagination",
            id="RESOURCES-LIST-2",
        ),
        MCPRequirement(
            feature="resources/list",
            level="MUST",
            description="Each resource MUST have required fields",
            id="RESOURCES-LIST-3",
        ),
    ],
    "resources/read": [
        MCPRequirement(
            feature="resources/read",
            level="MUST",
            description="Server MUST return valid content structure",
            id="RESOURCES-READ-1",
        ),
        MCPRequirement(
            feature="resources/read",
            level="MUST",
            description="Content MIME type MUST match listing",
            id="RESOURCES-READ-2",
        ),
        MCPRequirement(
            feature="resources/read",
            level="MUST",
            description="Server MUST handle errors correctly",
            id="RESOURCES-READ-3",
        ),
    ],
    "resources/templates": [
        MCPRequirement(
            feature="resources/templates",
            level="MUST",
            description="Server MUST return valid template structure",
            id="RESOURCES-TEMPLATES-1",
        ),
        MCPRequirement(
            feature="resources/templates",
            level="MUST",
            description="Template URIs MUST follow correct format",
            id="RESOURCES-TEMPLATES-2",
        ),
        MCPRequirement(
            feature="resources/templates",
            level="SHOULD",
            description="Template MIME types SHOULD be valid",
            id="RESOURCES-TEMPLATES-3",
        ),
    ],
    "resources/list_changed": [
        MCPRequirement(
            feature="resources/list_changed",
            level="SHOULD",
            description="Server SHOULD declare listChanged capability",
            id="RESOURCES-LIST-CHANGED-1",
        ),
        MCPRequirement(
            feature="resources/list_changed",
            level="SHOULD",
            description="Server SHOULD emit notification when list changes",
            id="RESOURCES-LIST-CHANGED-2",
        ),
    ],
    "resources/subscribe": [
        MCPRequirement(
            feature="resources/subscribe",
            level="SHOULD",
            description="Server SHOULD declare subscribe capability",
            id="RESOURCES-SUBSCRIBE-1",
        ),
        MCPRequirement(
            feature="resources/subscribe",
            level="SHOULD",
            description="Server SHOULD handle subscription lifecycle",
            id="RESOURCES-SUBSCRIBE-2",
        ),
        MCPRequirement(
            feature="resources/subscribe",
            level="MUST",
            description="Server MUST handle subscription errors",
            id="RESOURCES-SUBSCRIBE-3",
        ),
    ],
}
