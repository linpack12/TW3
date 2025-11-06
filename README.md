TW3 AI Web Automation and Intelligent Scrpaing
A fullstack solution consisting of an MCP server for web automation and an intelligent web scrpaing agent. 

Project Overview
This project is divided into two main parts:

Part 1: MCP Server - Web Automation Platform
An HTTP-based MCP server that exposes browser autmation tools, allowing AI agents ro interact with web pages. 

Part 2: Intelligent Scraping Agent - Structured Data Extraction
An intelligent agent built on top of the MCP server from part 1 that can extract structured data from dynamic web pages following a JSON schema, with automatic selector identification, type conversion, and pagination support. 

Key Features 
Part 1: MCP Server 
- Web Navigation - Navigate to URLs with error handling
- Screenshots - Capture viewpoert or full page screenshots
- Link Extraction - Extract all hyperlinks with optional filtering
- Form Handling - Fill form fields safely with validation
- Element Interaction - Click elements with error handling
- HTML Retrieval - Get rendered HTML after JavaScript execution

Part 2: Intelligent Scraping Agent
- Schema Analysis - Automatically analyze JSON schemas
- Selector Identifaction - Intelligently identify robust CSS selectors(data-* attributes, aria-labels, semantic tags)
- Automatic Type Conversion - Convert data(string -> number, boolean, datetime)
- Data Extraction & Validation - Extract and validate data with quality reporting 
- Pagination Support - Autmatically detect and follow pagination links
- User Interactions - Support for click, wait, and scroll actions
- Quality Reporting - Completion rates, missing fields, error tracking
- Retry Logic - Configurable retry mechanism for failed operations

Quick Start

Option 1: Docker
Build the image
- docker build -t tw3

Run Part 1 Demo
- docker run tw3 demo:part1

Run Part 2 Demo
- docker run tw3 demo:part2

Run Complete Demo(Part 1 + Part 2)
- docker run tw3 demo:all

Start MCP Server
- ocker run -p 8000:8000 tw3 server

Start MCP Server + HTTP Server (for Part 2 local testing)
- docker run -p 8000:8000 -p 8888:8888 tw3 server:http

Option 2: Docker Compose

Run Part 1 Demo
- docker-compose --profile demo run demo-part1

Run Part 2 Demo
- docker-compose --profile demo run demo-part2

Run Complete Demo
- docker-compose --profile demo run demo-all

Start MCP Server
- docker-compose up mcp-server

Start Scraping Agent Server
- docker-compose --profile scraping up scraping-agent

Option 3: Local Development (Without Docker)
Setup
#create virtual enironment
- python -m venv .venv
- source .venv/bin/activate or on windows -> - .venv\Scripts\Activate.ps1

#install dependencies
- pip install -r requirements.txt
- playwright install chromium

Run Part 1 Demo
#terminal 1:
- uvicorn src.mcp_server.app:app
#terminal 2: 
- python demo.py

Run Part 2 Demo
#terminal 1 - start MCP Server
- uvicorn src.mcp_server.app:app
#terminal 2 - start HTTP server (for local HTML testing)
- python run_local_server.py
#terminal 3 - run demo 
python demo_part_2.py

Project Structure
TW3/
|├── diagrams/
│   ├── Azure_Architecture_diagram_jpeg.jpg # Part 3: Diagram JPEG-format
|   ├── Azure_Architecture_Diagram.svg # Part 3: Diagram SVG-format
|
├── src/
│   ├── mcp_server/                    # Part 1: MCP Server
│   │   ├── app.py                     # FastAPI endpoints
│   │   ├── browser.py                 # Playwright browser management
│   │   ├── tools.py                   # Browser automation tools
│   │   └── schemas.py                 # Pydantic response schemas
│   │
│   └── agent/                         # Part 2: Scraping Agent
│       ├── agent.py                   # Main scraping orchestrator
│       ├── config_models.py           # Configuration models
│       ├── schema_analyser.py         # Schema analysis
│       ├── select_planner.py          # Selector identification
│       ├── extractor.py               # Data extraction logic
│       ├── result_formatter.py        # Output formatting
│       ├── mcp_client.py              # MCP communication
│       └── retry.py                   # Retry logic
│
├── artifacts/                         # Generated output
│   ├── json_dumps/                    # JSON extraction results
│   ├── html_dumps/                    # HTML captures
│   └── screenshots/                   # Screenshots
│
├── demo.py                            # Part 1: MCP Server demo
├── demo_part_2.py                     # Part 2: Scraping Agent demo
├── run_local_server.py                # HTTP server for local testing
│
├── page1.html                         # Test data for Part 2
├── page2.html                         # Test data for Part 2
│
├── Dockerfile                         # Container definition
├── docker-compose.yml                 # Multi-service orchestration
├── start.sh                           # Entry point script
├── requirements.txt                   # Python dependencies
│
├── DECISIONS.md                       # Technical decisions documentation
├── README.md                          # This file
├── .gitignore                         # Git ignore rules
└── LICENSE                            # License

Manual API Testing
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

Extract links
- curl -X POST http://127.0.0.1:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"tool": "extract_links", "params": {}}'


Generated artifacts are saved to:
Screenshots: artifacts/screenshots/
HTML dumps: artifacts/html_dumps/
JSON results: artifacts/json_dumps/
