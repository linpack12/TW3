import asyncio
from typing import Optional
from src.agent.config_models import ScrapeConfig
from src.agent.mcp_client import MCPClient

class ScrapeAgent:
    
    def __init__(self, client: MCPClient, config: ScrapeConfig):
        self.client = client
        self.config = config
    
    async def run_navigation(self) -> str:
        print(f"[Agent] Navigating to {self.config.url}")
        await self.client.navigate(str(self.config.url))

        if self.config.interactions:
            print(f"[Agent] Running {len(self.config.interactions)} interactions(s)...")
            await self._run_interactions()
        else:
            print("[Agent] No interactions defined.")
        
        print("[Agent] Fetching HTML...")
        html = await self.client.html()
        return html

    async def _run_interactions(self):
        for interaction in self.config.interactions:
            t = interaction.type.lower()
            print(f"[Agent] -> {t}")

            if t == "click" and interaction.selector: 
                await self._handle_click(interaction.selector)
            
            elif t == "wait" and interaction.duration:
                await self._handle_wait(interaction.duration)
            
            elif t == "scroll":
                await self._handle_scroll(interaction.direction or "bottom")
            
            else:
                print(f"[Agent] Skipping unknown or invalid interaction: {interaction}")
    
    async def _handle_click(self, selector: str):
        print(f"[Agent] Clicking on {selector}")
        await self.client.click(selector=selector)
    
    async def _handle_wait(self, duration_ms: int):
        sec = duration_ms / 1000.0
        print(f"[Agent] Waiting for {sec:.1f} seconds...")
        await asyncio.sleep(sec)
    
    async def _handle_scroll(self, direction: str):
        print(f"[Agent] Scrolling {direction}")
        try: 
            await self.client.scroll(direction)
        except AttributeError:
            print("[Agent] Scroll tool not yet implemented on MCP — skipping for now.")