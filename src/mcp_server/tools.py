from .schemas import ToolResponse

class Tools: 
    def __init__(self, page):
        self.page = page

    async def navigate(self, url: str, timeout_ms: int = 20000) -> ToolResponse:
        try: 
            await self.page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
            return ToolResponse(ok=True, data={"url": url})
        except Exception as e:
            return ToolResponse(ok=False, error=str(e))
