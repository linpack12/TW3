from typing import Any, Optional
from pydantic import BaseModel

class ToolResponse(BaseModel): 
    ok: bool
    data: Optional[Any] = None
    error: Optional[str] = None

class ListResponse(BaseModel): 
    tools: list[str]

class CallRequest(BaseModel):
    tool: str
    params: dict