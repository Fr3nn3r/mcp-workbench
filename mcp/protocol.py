"""Protocol definitions for MCP."""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class Argument(BaseModel):
    """Argument definition for a prompt."""

    name: str
    description: str
    required: bool


class Prompt(BaseModel):
    """Prompt definition."""

    name: str
    description: str
    arguments: Optional[List[Argument]] = None


class PromptsListResult(BaseModel):
    """Result for prompts/list method."""

    prompts: List[Prompt]
    nextCursor: Optional[str] = None


class TextContent(BaseModel):
    """Text content in a message."""

    type: str = Field("text", const=True)
    text: str


class ImageContent(BaseModel):
    """Image content in a message."""

    type: str = Field("image", const=True)
    data: str  # base64
    mimeType: str


class ResourceContent(BaseModel):
    """Resource content in a message."""

    type: str = Field("resource", const=True)
    resource: Dict[str, str]  # must include uri, mimeType, and text/blob


class PromptMessage(BaseModel):
    """A message in a prompt."""

    role: str = Field(..., pattern="^(user|assistant)$")
    content: Union[TextContent, ImageContent, ResourceContent]


class PromptsGetResult(BaseModel):
    """Result for prompts/get method."""

    description: Optional[str] = None
    messages: List[PromptMessage] = Field(..., min_items=1)
