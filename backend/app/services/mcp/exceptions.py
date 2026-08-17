class MCPBaseError(Exception):
    """Base exception for all MCP-related errors."""
    pass

class MCPUnavailableError(MCPBaseError):
    """Raised when the MCP server cannot be reached or session fails to initialize."""
    pass

class MCPToolNotFoundError(MCPBaseError):
    """Raised when an requested tool does not exist on the MCP server."""
    pass

class MCPAuthorizationError(MCPBaseError):
    """Raised when the caller lacks authorization to access the requested resource/tool."""
    pass

class MCPToolExecutionError(MCPBaseError):
    """Raised when an MCP tool fails during server-side execution."""
    pass
