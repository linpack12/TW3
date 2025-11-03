import asyncio
from urllib.parse import urljoin
from datetime import datetime
from typing import Any, Dict, List

from bs4 import BeautifulSoup
from src.agent.config_models import ScrapeConfig
from src.agent.mcp_client import MCPClient
from src.agent.retry import retry_async
from src.agent.schema_analyser import SchemaAnalyser
from src.agent.select_planner import SelectorPlanner
from src.agent.extractor import Extractor
from src.agent.result_formatter import ResultFormatter

class ScrapeAgent:
    """
    Intelligent web scraping agent that:
    1. Analyzes schema
    2. Navigates and retrieves HTML
    3. Identifies selectors automatically
    4. Extracts and validates data
    5. Handles pagination
    6. Produces formatted output
    """
    
    def __init__(self, client: MCPClient, config: ScrapeConfig):
        self.client = client
        self.config = config
        self.schema_analyser: SchemaAnalyser | None = None
        self.formatter: ResultFormatter | None = None
    
    def _should_retry(self) -> bool:
        opts = self.config.options
        return opts.retry_failed if opts else False
    
    async def _call_with_retry(self, coro_factory, *, retries_if_on: int = 3):
        if self._should_retry():
            return await retry_async(coro_factory, retries=retries_if_on)
        else:
            return await coro_factory()
    
    # ===== STEP 1: Schema Analysis =====
    
    def analyze_schema(self) -> None:
        """Step 1: Analyze the provided schema."""
        print("[Agent] Step 1: Analyzing schema...")
        self.schema_analyser = SchemaAnalyser(self.config.schema)
        self.formatter = ResultFormatter(
            collection_name=self.schema_analyser.collection_name or "data",
            expected_fields=self.schema_analyser.item_fields
        )
        
        if self.schema_analyser.collection_name:
            print(f"[Agent] Collection: {self.schema_analyser.collection_name}")
            print(f"[Agent] Expected fields: {list(self.schema_analyser.item_fields.keys())}")
        else:
            print("[Agent] ⚠ Could not identify collection in schema")
    
    # ===== STEP 2: Navigation & Retrieval =====
    
    async def run_navigation(self) -> str:
        """Step 2: Navigate to URL and execute interactions."""
        print(f"[Agent] Step 2: Navigating to {self.config.url}")
        await self._call_with_retry(lambda: self.client.navigate(str(self.config.url)))

        if self.config.interactions:
            print(f"[Agent] Running {len(self.config.interactions)} interactions(s)...")
            await self._run_interactions()
        else:
            print("[Agent] No interactions defined")
        
        print("[Agent] Fetching HTML...")
        html = await self._call_with_retry(lambda: self.client.html())
        print(f"[Agent] HTML retrieved: {len(html)} chars")
        return html

    async def _run_interactions(self):
        """Execute user-defined interactions (click, wait, scroll)."""
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
                print(f"[Agent] ⚠ Unknown interaction: {interaction}")
    
    async def _handle_click(self, selector: str):
        if self._should_retry():
            return await retry_async(
                lambda: self.client.click(selector=selector),
                retries=1,
                base_delay=0.3
            )
        await self.client.click(selector=selector)
    
    async def _handle_wait(self, duration_ms: int):
        sec = duration_ms / 1000.0
        print(f"[Agent] Waiting for {sec:.1f} seconds...")
        await asyncio.sleep(sec)
    
    async def _handle_scroll(self, direction: str):
        try:
            await self._call_with_retry(lambda: self.client.scroll(direction))
        except AttributeError:
            print("[Agent] ⚠ Scroll not implemented")
    
    # ===== STEP 3: Selector Identification =====
    
    def identify_selectors(self, html: str) -> SelectorPlanner:
        """Step 3: Identify CSS selectors for each field."""
        print(f"[Agent] STEP 3: IDentifying selectors...")
        
        if not self.schema_analyser:
            raise RuntimeError("Schema not analyzed. Call analyze_schema() first.")
        
        planner = SelectorPlanner(
            html=html,
            collection_name=self.schema_analyser.collection_name,
            expected_fields=self.schema_analyser.item_fields
        )
        plan = planner.build_plan()
        
        print(f"[Agent] ✓ Item selector: {plan.item_selector or 'None (document root)'}")
        print(f"[Agent] ✓ Field selectors identified for {len(plan.field_selectors)} fields")
        
        return plan
    
    # ===== STEP 4: Extraction & Validation =====
    
    def extract_data(self, html: str, selector_plan) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Step 4: Extract and validate data."""
        print(f"[Agent] STEP 4: Extracting data...")
        
        if not self.schema_analyser:
            raise RuntimeError("Schema not analyzed.")
        
        extractor = Extractor(
            html=html,
            selector_plan=selector_plan,
            field_types=self.schema_analyser.item_fields
        )
        items, quality_info = extractor.run()
        
        print(f"[Agent] ✓ Extracted {len(items)} items")
        if quality_info["missing_items"]:
            missing_count = sum(1 for m in quality_info["missing_items"] if m)
            if missing_count > 0:
                print(f"[Agent] ⚠ {missing_count} items have missing fields")
        
        return items, quality_info
    
    # ===== STEP 5: Pagination =====
    
    async def run_with_pagination(self) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Step 5: Execute full pipeline with pagination support.
        Returns aggregated items and quality info.
        """
        # Step 1: Analyze schema (only if not done)
        if not self.schema_analyser:
            self.analyze_schema()
        
        # Step 2: Navigate to first page
        all_items: List[Dict[str, Any]] = []
        all_missing: List[List[str]] = []
        
        first_html = await self.run_navigation()
        
        # Step 3: Identify selectors
        selector_plan = self.identify_selectors(first_html)
        
        # Step 4: Extract data
        items, quality_info = self.extract_data(first_html, selector_plan)
        all_items.extend(items)
        all_missing.extend(quality_info["missing_items"])
        
        # Step 5: Pagination (if enabled)
        opts = self.config.options
        if opts and opts.pagination:
            print(f"[Agent] STEP 5: Pagination enabled (max {opts.max_pages} pages)")
            
            max_pages = opts.max_pages or 1
            remaining = max(0, max_pages - 1)
            page_num = 1
            last_html = first_html

            while remaining > 0:
                print(f"[Agent] Fetching page {page_num + 1}...")
                
                next_href = self._find_next_link(last_html)
                if not next_href:
                    print("[Agent] ⚠ No next link found, stopping pagination")
                    break

                current = await self._call_with_retry(lambda: self.client.current_url())
                next_url = urljoin(current, next_href)

                await self._call_with_retry(lambda: self.client.navigate(next_url))
                if self.config.interactions:
                    await self._run_interactions()
                
                last_html = await self._call_with_retry(lambda: self.client.html())
                
                # Extract from this page
                page_items, page_quality = self.extract_data(last_html, selector_plan)
                all_items.extend(page_items)
                all_missing.extend(page_quality["missing_items"])
                
                print(f"[Agent] ✓ Page {page_num + 1}: +{len(page_items)} items")
                
                remaining -= 1
                page_num += 1
            
            print(f"[Agent] ✓ Pagination complete: {len(all_items)} items total")
        
        final_quality = {
            "total_items": len(all_items),
            "missing_items": all_missing
        }
        
        return all_items, final_quality
    
    # ===== STEP 6: Result Generation & Formatting =====
    
    async def run_complete(self) -> Dict[str, Any]:
        """
        Execute full pipeline: Schema → Navigate → Selectors → Extract → Paginate → Format.
        Returns formatted result according to specification.
        """
        try:
            print("\n" + "=" * 70)
            print("INTELLIGENT WEB SCRAPING AGENT - COMPLETE PIPELINE")
            print("=" * 70)
            
            # Ensure formatter is initialized first
            if not self.formatter:
                self.analyze_schema()
            
            # Run full pipeline
            all_items, quality_info = await self.run_with_pagination()
            
            # Generate metadata
            metadata = self._generate_metadata(all_items)
            
            # Format result - formatter is guaranteed to exist
            result = self.formatter.format_success(
                items=all_items,
                metadata=metadata,
                missing_items=quality_info["missing_items"]
            )
            
            print(f"\n[Agent] STEP 6: Result formatted")
            print(f"[Agent] ✓ Status: {result['status']}")
            print(f"[Agent] ✓ Total items: {result['quality_report']['total_items']}")
            print(f"[Agent] ✓ Completion rate: {result['quality_report']['completion_rate']:.1%}")
            print("\n" + "=" * 70)
            
            return result
        
        except Exception as e:
            print(f"\n[Agent] ✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Ensure formatter exists for error response
            if not self.formatter:
                self.analyze_schema()
            
            if self.formatter:
                return self.formatter.format_error(
                    error_message=str(e),
                    error_details=type(e).__name__
                )
            
            # Fallback if formatter still doesn't exist
            return {
                "status": "error",
                "error": str(e),
                "details": type(e).__name__,
                "data": None,
                "quality_report": None
            }
    
    def _generate_metadata(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate metadata for the extraction."""
        metadata = {
            "extraction_date": datetime.utcnow().isoformat() + "Z",
            "num_results": len(items),
            "source_url": str(self.config.url)
        }
        return metadata
    
    def _find_next_link(self, html: str) -> str | None:
        """Find next page link using multiple strategies."""
        soup = BeautifulSoup(html, "lxml")
        
        # Strategy 1: rel='next'
        a = soup.select_one("a[rel='next']")
        if a and a.get("href"):
            return a["href"]
        
        # Strategy 2: aria-label containing 'next'
        a = soup.select_one("a[aria-label*='next' i]")
        if a and a.get("href"):
            return a["href"]
        
        # Strategy 3: Text matching 'next'
        for cand in soup.select("a[href]"):
            txt = cand.get_text(strip=True).lower()
            if txt in {"next", "next page"} or txt.endswith("»") or "next" in txt:
                return cand["href"]
        
        # Strategy 4: Common pagination patterns
        a = soup.select_one("li.next a[href], .pagination a.next[href], .pager a.next[href]")
        if a and a.get("href"):
            return a["href"]
        
        return None