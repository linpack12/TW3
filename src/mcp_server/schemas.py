from typing import Any, Optional
from pydantic import BaseModel

# Standard response from a tool execution 
class ToolResponse(BaseModel): 
    ok: bool # True if the tool call succeeded, False if an error occurred
    data: Optional[Any] = None # Optional result data returned by the tool
    error: Optional[str] = None # Optional error message if the call failed

# Lists available tools from the MCP Server
class ListResponse(BaseModel): 
    tools: list[str] # List of tool names registered and exposed by the MCP server

# Request model sent by the MCP client aka Agent to invoke a specific tool 
class CallRequest(BaseModel):
    tool: str # Name of the tool to call
    params: dict # Arguments passed to the tool