from typing import List, Optional, Union, Dict
from pydantic import BaseModel


class PromptArgument(BaseModel):
    name: str
    description: str
    required: bool


class PromptDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    arguments: Optional[List[PromptArgument]] = None


class PromptsListResult(BaseModel):
    prompts: List[PromptDefinition]
    nextCursor: Optional[str] = None


# Models for prompts/get
class TextContent(BaseModel):
    type: str = "text"
    text: str


class ImageContent(BaseModel):
    type: str = "image"
    data: str
    mimeType: str


class ResourceContent(BaseModel):
    type: str = "resource"
    resource: Dict[str, str]  # uri, mimeType, text/blob


class PromptMessage(BaseModel):
    role: str
    content: Union[TextContent, ImageContent, ResourceContent]


class PromptsGetResult(BaseModel):
    description: Optional[str] = None
    messages: List[PromptMessage]
