"""Schema definitions for MCP protocol."""

from typing import Dict, List, Optional, Union, Literal, Annotated
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

    type: Literal["text"]
    text: str


class ImageContent(BaseModel):
    """Image content in a message."""

    type: Literal["image"]
    data: str  # base64
    mimeType: str


class ResourceContent(BaseModel):
    """Resource content in a message."""

    type: Literal["resource"]
    resource: Dict[str, str]  # must include uri, mimeType, and text/blob


MessageContent = Annotated[
    Union[TextContent, ImageContent, ResourceContent], Field(discriminator="type")
]


class PromptMessage(BaseModel):
    """A message in a prompt."""

    role: Literal["user", "assistant"]
    content: MessageContent


class PromptsGetResult(BaseModel):
    """Result for prompts/get method."""

    description: Optional[str] = None
    messages: List[PromptMessage] = Field(..., min_length=1)
