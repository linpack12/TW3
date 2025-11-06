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
        # Save all screenshots for debugging
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
        
    async def extract_links(self, filter: str | None = None) -> ToolResponse:
        try: 
            # Retreieve dict with link and associated text
            links = await self.page.eval_on_selector_all(
                "a",
                """els => els.map(a => ({
                    text: a.innerText.trim(),
                    href: a.href
                }))"""
            )

            # Filter 
            if filter: 
                filter_lower = filter.lower()
                links = [
                    link for link in links
                    if filter_lower in link["text"].lower() or filter_lower in link["href"].lower()
                ]
            
            return ToolResponse(ok=True, data=links)
        
        except Exception as e: 
            return ToolResponse(ok=False, error=str(e))
        
    async def fill_field(self, selector: str, value: str) -> ToolResponse:
        try: 
            locator = self.page.locator(selector)
            
            is_editable = await locator.is_editable()
            if not is_editable:
                return ToolResponse(ok=False, error=f"Element '{selector}' is not editable")
            
            # Fill field with value 
            await locator.fill(value)

            return ToolResponse(ok=True, data={"selector": selector, "value": value})
     
        except Exception as e: 
            return ToolResponse(ok=False, error=str(e))
    
    async def click(self, selector: str) -> ToolResponse:
        try:
            locator = self.page.locator(selector)

            # Count number of matches
            count = await locator.count()
            # Selector was not found on page 
            if count == 0: 
                return ToolResponse(ok=False, error=f"Element '{selector}' not found on page")
            # Found to many corresponding selectors -> need to narrow it down
            if count > 1: 
                return ToolResponse(ok=False, error=f"Selector '{selector}' matched {count} elements. Please provice a more specific selector.")
            
            single_element = locator.nth(0)
            # Check if we can click on it 
            if not await single_element.is_enabled():
                return ToolResponse(ok=False, error=f"Element '{selector}' is visible but disabled")
            
            await single_element.click()

            return ToolResponse(ok=True, data={"selector": selector})
     
        except Exception as e:
            return ToolResponse(ok=False, error=str(e)) 
    
    async def html(self, out_dir: str= "artifacts/html_dumps", file_name: str | None = None) -> ToolResponse: 
        try: 
            markup = await self.page.content()
            # Save html dumps for debugging
            out_path = Path(out_dir)
            out_path.mkdir(parents=True, exist_ok=True)

            if not file_name: 
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"page_{stamp}.html"
            
            file_path = out_path / file_name
            # Write the result into the target file
            file_path.write_text(markup, encoding="utf-8")

            return ToolResponse(ok=True, data={"html_path": str(file_path), "message": "HTML saved successfully", "html": markup})
        
        except Exception as e:
            return ToolResponse(ok=False, error=str(e))
    
    async def scroll(self, direction: str = "bottom") -> ToolResponse:
        # Scroll in the target direction (bottom/top)
        try: 
            if direction == "top":
                await self.page.evaluate("window.scrollTo(0, 0);")
            else:
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            
            return ToolResponse(ok=True, data={"direction": direction})
        
        except Exception as e:
            return ToolResponse(ok=False, error=str(e))
        
    async def current_url(self) -> ToolResponse:
        try: 
            return ToolResponse(ok=True, data={"url": self.page.url})
        except Exception as e:
            return ToolResponse(ok=False, error=str(e))

