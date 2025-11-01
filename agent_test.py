import asyncio
from src.agent.mcp_client import MCPClient
from src.agent.agent import ScrapeAgent
from src.agent.config_models import ScrapeConfig

async def main():
    client = MCPClient(base_url="http://127.0.0.1:8000")
    await client.start()

    try: 
        print("1) navigate to example.com")
        nav = await client.navigate("https://example.com")
        print(nav)

        print("\n2) get html")
        html = await client.html()
        print(html[:200], "...")

        print("\n3) extract links")
        links = await client.extract_links()
        print(links)

        print("\n4) Run ScrapeAgent (Navigation + Interactions + HTML Retrieval)")
        sample_config= {
            "url": "https://example.com",
            "schema": {"dummy": "string"},
            "interactions": [
                {"type": "wait", "duration": 1000},
                {"type": "scroll", "direction": "bottom"}
            ],
            "options": {"pagination": False}
        }

        cfg = ScrapeConfig(**sample_config)
        agent = ScrapeAgent(client, cfg)
        final_html = await agent.run_navigation()
        print(f"\n[Agent] final HTML length: {len(final_html)} chars")
    
    finally:
        await client.stop()

if __name__ == "__main__":
    asyncio.run(main())