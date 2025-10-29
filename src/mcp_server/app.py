from .browser import BrowserManager
from .tools import Tools
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from .schemas import ToolResponse, ListResponse, CallRequest

TOOLS = ["navigate", "screenshot", "extract_links", "fill_field", "click", "html"]

browser = BrowserManager(headless=True)
tools: Tools | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    await browser.start()
    global tools
    tools = Tools(browser.page)
    try: yield
    finally: 
        await browser.stop()

app = FastAPI(lifespan=lifespan)

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
    
    assert tools is not None
    handler = getattr(tools, req.tool)
    result: ToolResponse = await handler(**req.params)
    return result
