from fastapi import FastAPI, HTTPException
from .schemas import ToolResponse, ListResponse, CallRequest

TOOLS = ["navigate", "screenshot", "extract_links", "fill_field", "click", "html"]

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/mcp/initialize")
async def mcp_initialize():
    return {"status": "ok", "protocol": "mcp-sse", "tools": TOOLS}

@app.get("/mcp/tools/list", response_model=ListResponse)
async def get_mcp_tools():
    return ListResponse(tools=TOOLS)

@app.post("/mcp/tools/call", response_model=ToolResponse)
async def call_tool(req: CallRequest):
    if req.tool not in TOOLS:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {req.tool}")
    
    return ToolResponse(ok=True, data={"tool": req.tool, "params": req.params})
