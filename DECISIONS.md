#DECISIONS.md

##Overall Architecture
The project is structured around a single FastApi application exposing the MCP endpoints:
    - /mcp/initialize
    - /mcp/tools/list
    - /mcp/tools/call

All tools share a single Playwright page instance, managed through a browsermanager 'broswer.py' class.
This makes the server stateful across multiple requests while staying thread-safe within the async event loop. 

I thought this deisgn made it simplistic and scalable: 
    - Easy to add new tools by extending 'Tools'
    - Centralized browser lifecycle management
    - Uniform responses across all endpoints
    - Seperation between transport layer FastAPI and logic with Playwirght tools

The structure made it eaiser for me to learn and develop in python since it is a fairly new language for me! 

I choose FastApi and Uvicorn because from what I read it was modern and fully asynchronous. 
Other benefits of it is its easy request validation and native Pydantic integration. 
And Playwright also seemed like the modern choice from reading and understanding the current state of pyton AI development since it has built in support for things like async, screenshots, selectors, and navigation events. 

I implemented a uniform response schema which means every tool returns a standardized object. This ensures that both we and AI agents can process responses consistently regardless of which tool is used. It also simplifies error handling which is always nice. 
Further all responses and requests use Pydantic models to ensure data consistency between client and server and prevents runtime errors from malformed inputs. 

I chose to not rely on Playwright excpetions and had all methods catch errors and return a ToolResponse given the current error which goes hand in hand with the requirement in the assignment. 

Since I was time limited and work a full time job currently I designed each tool to meet the exact behavior described in the assignment and read them very carefully so I did not waste time. 

I choose to make a dockerfile since I wanted to make the reviewer and tester experience as simple as possible, I would love it to only be one command to build and test everything. 

The script start.sh runs the server in the background during demo mode, executes the demo.py workflow, then shuts it down autmatically. This provides a clean, reproducible test without requiring the user to set up Python locally. 

My workprocces was as follows: 
    1. Implemented core MCP endpoints.
    2. Added navigate and verified playwright intergration. 
    3. Implemendted and testet each separately. 
    4. Created the mandatory demo scenario.
    5. Added Docker support with dual run modes. 
    6. Verified all features inside the container. 

