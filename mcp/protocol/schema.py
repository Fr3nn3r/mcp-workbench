"""Schema definitions for MCP protocol."""

from typing import Dict, List, Optional, Union, Literal, Annotated, Any
from pydantic import BaseModel, Field, ConfigDict


class JsonRpcRequest(BaseModel):
    """Base JSON-RPC request model."""

    jsonrpc: Literal["2.0"]
    id: Optional[Union[int, str]] = None
    method: str
    params: Optional[Dict[str, Any]] = None


class JsonRpcResponse(BaseModel):
    """Base JSON-RPC response model."""

    jsonrpc: Literal["2.0"]
    id: Optional[Union[int, str]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="allow")

    def dict(self, *args, **kwargs):
        # Ensure either result or error is present, but not both
        d = super().dict(*args, **kwargs)
        if d.get("error") is None:
            d.pop("error", None)
        if d.get("result") is None and d.get("error") is None:
            d["result"] = {}
        return d


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


class Resource(BaseModel):
    """A resource exposed by the server."""

    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None


class TextResourceContent(BaseModel):
    """Text content of a resource."""

    type: Literal["resource_text"]
    uri: str
    mimeType: str
    text: str


class BlobResourceContent(BaseModel):
    """Binary content of a resource."""

    type: Literal["resource_blob"]
    uri: str
    mimeType: str
    blob: str


ResourceContent = Union[TextResourceContent, BlobResourceContent]


class ResourceTemplate(BaseModel):
    """A parameterized resource template."""

    uriTemplate: str
    name: str
    description: Optional[str] = None
    mimeType: str


class ResourcesListResult(BaseModel):
    """Result of resources/list method."""

    resources: List[Resource]
    nextCursor: Optional[str] = None


class ResourcesReadResult(BaseModel):
    """Result of resources/read method."""

    contents: List[ResourceContent]


class ResourcesTemplatesListResult(BaseModel):
    """Result of resources/templates/list method."""

    resourceTemplates: List[ResourceTemplate]


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


class Tool(BaseModel):
    """Tool definition."""

    name: str
    description: str
    inputSchema: dict


class ToolCallResult(BaseModel):
    """Result of a tool call."""

    content: List[MessageContent]
    isError: Optional[bool] = False


class CompletionResult(BaseModel):
    """Result of a completion request."""

    completion: dict  # contains values, hasMore, total


class ToolsListResult(BaseModel):
    """Result of tools/list method."""

    tools: List[Tool]
    nextCursor: Optional[str] = None
