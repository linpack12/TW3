from playwright.async_api import async_playwright, Page, Browser, BrowserContext

class BrowserManager: 
    def __init__(self, headless: bool = True):
        self._pw = None
        self.browser: Browser | None = None
        self.ctx: BrowserContext | None = None
        self.page: Page | None = None
        self._headless = headless
    
async def start(self):
    self._pw = await async_playwright().start()
    self.browser = await self._pw.chromium.launch(headless=self._headless)
    self.ctx = await self.browser.new_context()
    self.page = await self.ctx.new_page()

async def stop(self):
    if self.ctx: 
        await self.ctx.close()
    if self.browser: 
        await self.browser.close()
    if self._pw:
        await self._pw.stop()
