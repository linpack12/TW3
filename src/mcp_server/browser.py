from playwright.async_api import async_playwright, Page, Browser, BrowserContext

# Handles Playwright browser lifecycle for the MCP server
class BrowserManager: 
    def __init__(self, headless: bool = True):
        self._pw = None # Playwright driver instance
        self.browser: Browser | None = None # Chromium browser instance
        self.ctx: BrowserContext | None = None # Isolated browser context 
        self.page: Page | None = None # Active page object used by MCP tools
        self._headless = headless # Run browser in headless mode 
    
    # Launch a new headless Chromium session 
    async def start(self):
        self._pw = await async_playwright().start()
        self.browser = await self._pw.chromium.launch(headless=self._headless)
        self.ctx = await self.browser.new_context()
        self.page = await self.ctx.new_page()

    # Close page, context and browser on shutdown
    async def stop(self):
        if self.ctx: 
            await self.ctx.close()
        if self.browser: 
            await self.browser.close()
        if self._pw:
            await self._pw.stop()
