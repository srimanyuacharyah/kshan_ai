import time
import json
from typing import Dict, Any, List, Optional
from mcp_server.app.server import mcp_server
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.services.mcp.exceptions import (
    MCPUnavailableError,
    MCPToolNotFoundError,
    MCPAuthorizationError,
    MCPToolExecutionError
)
from backend.app.services.mcp.schemas import (
    MCPToolInfo,
    MCPToolCallResult,
    MCPHealthStatus
)

class KshanMCPClient:
    """
    Official MCP Client adapter for KSHAN:
    Connects to KSHAN Multiverse Context Server over Streamable HTTP or direct memory transport.
    """

    def __init__(self, server_url: Optional[str] = None):
        self.server_url = server_url or settings.MCP_SERVER_URL
        self._server = mcp_server

    async def list_tools(self) -> List[MCPToolInfo]:
        """Discover registered tools on the MCP server."""
        try:
            tools = await self._server.list_tools()
            result = []
            for t in tools:
                result.append(
                    MCPToolInfo(
                        name=t.name,
                        description=t.description,
                        input_schema=t.input_schema if hasattr(t, "input_schema") else {}
                    )
                )
            logger.info(f"Discovered {len(result)} tools on MCP server.")
            return result
        except Exception as e:
            logger.error(f"Failed to list MCP tools: {e}", exc_info=True)
            raise MCPUnavailableError(f"Cannot communicate with MCP server: {str(e)}")

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        auth_token: Optional[str] = None
    ) -> MCPToolCallResult:
        """
        Invoke an MCP tool with authenticated user context.
        Injects auth_token into arguments to enforce tenant isolation.
        """
        start = time.perf_counter()
        call_args = dict(arguments)
        if auth_token:
            call_args["auth_token"] = auth_token

        logger.info(f"Invoking MCP tool '{tool_name}' with {len(call_args)} arguments...")

        try:
            # Check tool existence
            tools = await self._server.list_tools()
            available = {t.name for t in tools}
            if tool_name not in available:
                raise MCPToolNotFoundError(f"MCP tool '{tool_name}' not found on server.")

            # Call tool through MCP server
            res = await self._server.call_tool(tool_name, call_args)
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

            # Unpack result
            data = None
            if hasattr(res, "content") and res.content:
                first_content = res.content[0]
                if hasattr(first_content, "text"):
                    try:
                        data = json.loads(first_content.text)
                    except Exception:
                        data = first_content.text
                else:
                    data = first_content
            elif hasattr(res, "data"):
                data = res.data
            else:
                data = res

            # Check if returned error dict
            if isinstance(data, dict) and "error" in data:
                err_text = data["error"]
                if "Unauthorized" in err_text or "Authentication required" in err_text:
                    raise MCPAuthorizationError(err_text)
                raise MCPToolExecutionError(err_text)

            logger.info(f"MCP tool '{tool_name}' completed successfully in {elapsed_ms}ms.")
            return MCPToolCallResult(
                tool_name=tool_name,
                success=True,
                data=data,
                execution_time_ms=elapsed_ms
            )

        except (MCPToolNotFoundError, MCPAuthorizationError) as e:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.warning(f"MCP security/not-found error on '{tool_name}': {e}")
            raise
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            err_msg = str(e)
            if "Unauthorized" in err_msg or "Authentication required" in err_msg or "auth_token" in err_msg or "Field required" in err_msg:
                logger.warning(f"MCP authorization failure on '{tool_name}': {err_msg}")
                raise MCPAuthorizationError(err_msg)
            logger.error(f"MCP tool '{tool_name}' failed after {elapsed_ms}ms: {e}", exc_info=True)
            raise MCPToolExecutionError(f"Tool execution failed: {str(e)}")

    async def read_resource(self, uri: str, auth_token: str = "") -> str:
        """Read an MCP resource securely."""
        try:
            res = await self._server.read_resource(uri)
            if hasattr(res, "contents") and res.contents:
                return res.contents[0].text
            return str(res)
        except Exception as e:
            logger.error(f"Failed to read MCP resource '{uri}': {e}")
            raise MCPToolExecutionError(f"Resource read error: {str(e)}")

    async def check_connection(self) -> MCPHealthStatus:
        """Health and connectivity check for MCP server."""
        try:
            tools = await self.list_tools()
            tool_names = [t.name for t in tools]
            return MCPHealthStatus(
                connected=True,
                server_name=self._server.name,
                tools_count=len(tool_names),
                tools=tool_names
            )
        except Exception as e:
            return MCPHealthStatus(
                connected=False,
                error=str(e)
            )

mcp_client = KshanMCPClient()
