# TW3 MCP Server
This project is built as part of a technical assigment for TW3Partners. 

##Features 
The mcp server exposes a suite of browser autmation tools over HTTP, enabling the AI agensts to: 
    - Navigate to URLs
    - Take screenshots (viewport or full-page)
    - Extract all hyperlinks
    - Fill form fields safely
    - Click elements
    - Retrieve rendered HTML

All tools conform to a **uniform response schema**:
```json
{
  "ok": true,
  "data": { ... },
  "error": null
}
```

##Quick Start (Docker)

This is the recommended way to run and test the demo for part 1.

Build the image
- docker builld -t tw3-mcp .

Run in server mode - This starts the MCP API and exposes it on port 8000.
- docker run --rm -p 8000:8000 tw3-mcp

Run in demo mode - This automatically runs the Mandatory Test Scenario: 
    a) Navigate to https://example.com  
    b) Take a screenshot
    c) Extract all links
    d) Navigate to the first link
    e) Take another screenshot

- docker run --rm tw3-mcp demo

Two screenshots will be created inside the container at: /app/artifacts/screenshots/

To save them locally, mount a volume: docker run --rm -v ${PWD}/artifacts/screenshots:/app/artifacts/screenshots tw3-mcp demo

Screenshots will appear under: ./artifacts/screenshots/

##Manual Testing (local requests)

List available tools
    - curl http://127.0.0.1:8000/mcp/tools/list

Navigate to a page
    - curl -X POST http://127.0.0.1:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"tool": "navigate", "params": {"url": "https://example.com"}}'

Take a screenshot
- curl -X POST http://127.0.0.1:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"tool": "screenshot", "params": {"full_page": true}}'

Available Tools: 
    - navigate
    - screenshot
    - extract_links
    - fill_field
    - click
    - html

##Architecture Overview
src/
└── mcp_server/
    ├── app.py          → FastAPI endpoints for MCP protocol
    ├── tools.py        → Browser automation methods (Playwright)
    ├── browser.py      → Manages Chromium context & page
    ├── schemas.py      → Pydantic models for uniform responses
    └── __init__.py

##Docker Entrypoint Modes
The container is controlled via the start.sh script
# Default server mode
docker run --rm -p 8000:8000 tw3-mcp

# Demo mode (runs full scenario)
docker run --rm tw3-mcp demo

Internally:
In server mode, it starts Uvicorn.

In demo mode, it starts Uvicorn in the background, runs demo.py, and stops the server automatically.

##Development (local)
If you prefer ro tun without Docker: 
    - python -m venv .venv
    - .\.venv\Scripts\Activate.ps1     # (Windows)
    - pip install -r requirements.txt
    - uvicorn src.mcp_server.app:app

Then visit:
http://127.0.0.1:8000/health

Run demo locally:
    - python demo.py

##Notes
start.sh uses LF line endings and has execute permissions to ensure Docker compatibility.
Playwright dependencies are installed automatically during the build.
To re-install Chromium manually inside the container:
    - playwright install chromium

