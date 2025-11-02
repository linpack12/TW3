import asyncio
from src.agent.mcp_client import MCPClient
from src.agent.agent import ScrapeAgent
from src.agent.config_models import ScrapeConfig
from src.agent.schema_analyser import SchemaAnalyser
from src.agent.select_planner import SelectorPlanner

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
        sample_config = {
            "url": "https://example.com/products",
            "schema": {
                "products": [
                    {
                        "name": "string",
                        "price": "number",
                        "description": "string",
                        "image_url": "string",
                        "availability": "boolean",
                        "specifications": {
                            "cpu": "string",
                            "ram": "string"
                        }
                    }
                ],
                "metadata": {
                    "extraction_date": "datetime",
                    "num_results": "number"
                }
            },
            "interactions": [
                {"type": "wait", "duration": 1000},
                {"type": "scroll", "direction": "bottom"}
            ],
            "options": {
                "pagination": True,
                "max_pages": 5,
                "retry_failed": True
            }
        }

        cfg = ScrapeConfig(**sample_config)
        agent = ScrapeAgent(client, cfg)
        final_html = await agent.run_navigation()
        print(f"\n[Agent] final HTML length: {len(final_html)} chars")

        analyser = SchemaAnalyser(cfg.schema)
        analyser.debug_print()

        planner = SelectorPlanner(html=final_html, collection_name=analyser.collection_name, expected_fields=analyser.item_fields,)
        plan = planner.build_plan()
        plan.debug_print()

    
    finally:
        await client.stop()

if __name__ == "__main__":
    asyncio.run(main())