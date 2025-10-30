from pathlib import Path
from datetime import datetime
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
    
    async def screenshot(self, full_page: 
        bool = False, file_name: str | None = None, 
        out_dir: str = "artifacts/screenshots", 
        quality: int | None = None, ) -> ToolResponse: 

        try: 
            out_path = Path(out_dir)
            out_path.mkdir(parents=True, exist_ok=True)

            if not file_name:
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"screenshot_{stamp}"
            
            #Choose format 
            if quality is not None: 
                file_path = out_path / f"{file_name}.jpg"
                await self.page.screenshot(path=str(file_path), full_page=full_page, quality=quality, type="jpeg",)
            else:
                file_path = out_path / f"{file_name}.png"
                await self.page.screenshot(path=str(file_path), full_page=full_page, type="png")
            
            return ToolResponse(
                ok=True,
                data={"path": str(file_path), "full_page": full_page}
            )
        
        except Exception as e: 
            return ToolResponse(ok=False, error=str(e))
        
