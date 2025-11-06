#DECISIONS.md

Part 1: MCP Server Architecture
##Overall Architecture
The project is structured around a single FastApi application exposing the MCP endpoints:
    - /mcp/initialize - initialize protocol
    - /mcp/tools/list - list available tools
    - /mcp/tools/call - execute a tool

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

My workprocces was as follows: 
    1. Implemented core MCP endpoints.
    2. Added navigate and verified playwright intergration. 
    3. Implemendted and testet each separately. 
    4. Created the mandatory demo scenario.
    5. Added Docker support with dual run modes. 
    6. Verified all features inside the container. 

Part 2: Intelligent Scraping Agent
I kept building on Part 1, I created a multi-stage scraping agent that orchestrates the MCP server to extract structured data. The agent follows a 6 step pipeline wich looks like this: Schema Analysis -> Navigation -> Selector ID -> Extraction -> Pagination -> Formatting

Key Components: 
Schema Analyzer 
- Parses JSON schema to understand data structure
- Flattens nested fiels for example specifications.cpu -> ["specifications", "cpu"]
- Identifies collection name and expected field types

Selector Planner
- Identifies CSS selectors for each field
- Uses a tiered approach where Tier 1 is most robust and Tier 3 is fallback
- Prioritzes robust selectors: data-* attributs, arial-label, semantic tags

I used multiple selector strategies instead of relying on a single selector which means i the first selector did not match we try alternatives which makes the agent more resilient to HTML structure changes. I read a lot about how to identfy css selectors and it seems like a lot of people uses a LLM for this step which makes sense since it becomes so much more clean than doing it manually. 

Extractor
- Extract data using identigied selectors
- Converts types according to schema (string -> number, boolean, datetime)
- Handles missing or invalid data 

Here i used BeatifulSoup with lxml parser for HTML which I read articles about being a fast parser. I also decided to separate the casting function for type conversion wich i think made the file and logic more clean and testable. 

Result Formatter
- Formats extraction results according to spec in pdf
- Generates quality metrics(completion rate, missing fiels)
- Creates both success and error responses 

I wanted to seperate the quality metrics from the extraction wich separated data collection from analysis, making the code more maintainable and clean. 

The part 2 development workflow was as follows:
- Started with schema analysis - understanding what data to extract
- Built selector identfication - implemented intelligent selector discovery
- Implemented extraction - data extraction with type conversion
- Added pagination -automatic multi page handling
- Built result formatting - quality metrics and structured output
- Created demos - + with real test HTML files
- Added JSON output - saves result to artifacts/json_dumps/

Docker
I chose Docker to make the reviwer and tester experience as simple as possible. 
Ideally only one command to build and test evertyhing. 

Benefits of that:
- No local python setup required 
- Consistent environment across all machines
- Easy reproducibility
- Simple for CI/CD integration

Entry Point Modes (start.sh) can be found in the readme.md 

I wanted to have flexible modes so testers can run specific parts or everything at once. 
I also included docker compose for multi-service orchestration which was suggested by a LLM.

I used AI to generate both docker files and run_local_server.py and comments on demo_part_2.py based on my comments for demo.py since I am not that familiar with docker but wanted to tests to be as easy for the tester as possible and it was not part of the test so I figured it was a good use case. 

Future Improvements
Simple selector discovery, as I said earlier integration with a call to a LLM to handle that or use ML would achieve even better selection. 
We could also have connection pooling which enables multiple browser instances with load balancing. Also cahcing, cache extracted data and selector strategies. Machine learning to have more accurate selectors over time. Lastely rate limiting to prevent abuse of the MCP server. 

Part 3: Azure Architecture Diagram
The workprocess for this part consisted of keeping focus on the given requirements and gathering information about what Azure and Microsoft offers as solutions. I watched a lot of microsoft azure own videos on agents and mcp servers and different ways of implementing them into the Azure architecure which really help me to develop a overview of what I should use and how. 

Most things are already described in the diagram but I thought it would be nice to have in text format as well. 

I will give a summary of requirements given and my solution here: 
Complete traceability of scraping - All jobs are logged in Cosmos DB and Blob Storage(WORM), with telemetry in Azure Monitor and Sentinel for monthly audits. 

Respect for robots.txt & rate limiting - Enforced via API Management policies, robots.txt caching and validation handled by workers.

Automatic IP rotation - Implemented through Azure NAT Gateway with static IP pools and automatic rotation. 

End to end encryption - TLS 1.2+ in transit, CMK encryption at rest through Azure Key Vault integration. 

Strict network segregation - Private Container App envoirment with Azure Firewall and no public DB endpoints.

Monthly security audits & centralized logs - Azure Monitor, Application Insights, Sentinel provide unified observability. 

Scalability (500-1000 users) - Azure Service Bus, autoscaling Container Apps, and Redis caching handle concurrent load. 

SLA 99.9% availability - Azure Fron Door (global load balancing) + geo redundant Cosmos/Blob + continer resilience. 

Backup & Recovery - Recovery Services Vault (RSV) with CMK encryption, immutability(WORM), and geo replication (GRS). 

Multi clod / Migration - You could to a off site copy to AWS S3/GCP stoarge which supports gradual migration from on-prem -> Azure -> multi region DR. 

This in the grand scheme means we achive a system with full compliance with GDPR and ISO 27001, supports enterprise observability, and maintins high availability through Azure PaaS based rudundancy. The deisgn is modular, scalable and autiable end to end. 

Was a lot of fun working on this mini project! 