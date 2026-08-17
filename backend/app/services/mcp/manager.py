from typing import Dict, Any, List, Optional
from backend.app.services.mcp.client import KshanMCPClient, mcp_client
from backend.app.services.mcp.schemas import MCPToolInfo, MCPToolCallResult, MCPHealthStatus

class MCPManager:
    """
    High-level manager for orchestrating MCP tool calls on behalf of the AI Orchestrator.
    Handles tool discovery caching and session diagnostics.
    """

    def __init__(self, client: Optional[KshanMCPClient] = None):
        self.client = client or mcp_client
        self._cached_tools: Optional[List[MCPToolInfo]] = None

    async def get_available_tools(self, force_refresh: bool = False) -> List[MCPToolInfo]:
        """Return available MCP tools with optional cache refresh."""
        if self._cached_tools is None or force_refresh:
            self._cached_tools = await self.client.list_tools()
        return self._cached_tools

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        auth_token: str
    ) -> MCPToolCallResult:
        """Execute a tool on behalf of the authenticated user."""
        return await self.client.call_tool(tool_name, arguments, auth_token=auth_token)

    async def get_health(self) -> MCPHealthStatus:
        """Check MCP server connectivity and tool readiness."""
        return await self.client.check_connection()

mcp_manager = MCPManager()
