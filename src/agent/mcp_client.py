from __future__ import annotations
from typing import Optional, Any
import httpx

# Raised when the MCP server returns an error response
class MCPError(Exception):
    pass

"""
Async client wrapper for communicating with the local MCP server. 
Internally all actions are routed through '_call_tool()' which matches the MCP API contract
"""
class MCPClient:

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        # Base URL of the MCP server, Defualts to a local dev instance
        self.base_url = base_url
        self._client: Optional[httpx.AsyncClient] = None

    # Creates an AsyncClient session that keeps the connection open for reuse across multiple tool calls
    async def start(self) -> None: 
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10)
    
    # Closes the underlying HTTP session when the agent shuts down
    async def stop(self) -> None: 
        if self._client is not None:
            await self._client.aclose()
            self._client = None
    
    # Internal method for invoking any MCP tool
    async def _call_tool(self, tool: str, params: dict[str, Any]) -> dict[str, Any]:
        assert self._client is not None

        payload = {"tool": tool, "params": params}
        response = await self._client.post(f"{self.base_url}/mcp/tools/call", json=payload)

        body = response.json()
        
        ok = body.get("ok", False)
        if not ok: 
            err = body.get("error", "Unknown MCP error")
            raise MCPError(f"{tool} failed: {err}")
        
        return body.get("data", {})
    
    # Public methods for the agent to use
    # Each corresponds 1:1 to a registered tool on the MCP server

    async def navigate(self, url: str) -> dict[str, Any]:
        return await self._call_tool("navigate", {"url": url})
    
    async def screenshot(self, full_page: bool = False) -> dict[str, Any]:
        return await self._call_tool("screenshot", {"full_page": full_page})
    
    async def extract_links(self, filter: Optional[str] = None) -> list[dict[str, str]]:
        params: dict[str, Any] = {}
        if filter:
            params["filter"] = filter
        
        data = await self._call_tool("extract_links", params)
        
        return data
    
    async def click(self, selector: str) -> dict[str, Any]:
        return await self._call_tool("click", {"selector": selector})
    
    async def fill_field(self, selector: str, value: str) -> dict[str, Any]: 
        return await self._call_tool("fill_field", {"selector": selector, "value": value})
    
    async def html(self) -> str:
        data = await self._call_tool("html", {})
        if isinstance(data, dict) and "html" in data:
            return data["html"]
        
        if isinstance(data, str): 
            return data
        
        return ""
    
    async def scroll(self, direction: str = "bottom"):
        payload = {"tool": "scroll", "params": {"direction": direction}}
        return await self._call_tool("scroll", payload["params"])
    
    async def current_url(self) -> str:
        data = await self._call_tool("current_url", {})
        return data.get("url", "")

