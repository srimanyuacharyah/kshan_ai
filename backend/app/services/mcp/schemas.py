from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class MCPToolInfo(BaseModel):
    name: str
    description: Optional[str] = None
    input_schema: Dict[str, Any] = Field(default_factory=dict)

class MCPToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)

class MCPToolCallResult(BaseModel):
    tool_name: str
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time_ms: float

class MCPHealthStatus(BaseModel):
    connected: bool
    server_name: Optional[str] = None
    tools_count: int = 0
    tools: List[str] = Field(default_factory=list)
    error: Optional[str] = None
