from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union

# JSON-RPC models
class JsonRpcRequest(BaseModel):
    jsonrpc: str
    method: str
    id: Union[str, int]
    params: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

class JsonRpcError(BaseModel):
    jsonrpc: str = "2.0"
    error: ErrorResponse
    id: Optional[Union[str, int]] = None

class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Any
    id: Union[str, int]

# MCP specific models
class MCPContentItem(BaseModel):
    type: str
    text: Optional[str] = None
    json: Optional[Dict[str, Any]] = None

class MCPToolCallResponse(BaseModel):
    content: List[MCPContentItem]
    isError: bool