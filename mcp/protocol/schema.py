from typing import List, Optional, Union, Dict, Any
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


# Models for resources/list
class Resource(BaseModel):
    uri: str
    name: str
    mimeType: Optional[str] = None
    description: Optional[str] = None


class ResourcesListResult(BaseModel):
    resources: List[Resource]
    nextCursor: Optional[str] = None


# Models for resources/read
class ResourceContent(BaseModel):
    uri: str
    mimeType: str
    text: Optional[str] = None
    blob: Optional[str] = None


class ResourcesReadResult(BaseModel):
    contents: List[ResourceContent]


# Models for resources/templates/list
class ResourceTemplate(BaseModel):
    uriTemplate: str
    name: str
    mimeType: str
    description: Optional[str] = None
    parameters: Optional[List[Dict[str, Any]]] = None


class ResourcesTemplatesListResult(BaseModel):
    resourceTemplates: List[ResourceTemplate]
    nextCursor: Optional[str] = None
