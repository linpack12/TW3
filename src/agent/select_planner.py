from __future__ import annotations
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup

class SelectorPlan:
    def __init__(self, item_selector: Optional[str], field_selectors: Dict[str, List[str]]):
        self.item_selector = item_selector
        self.field_selectors = field_selectors
    
    def debug_print(self) -> None:
        print("[SelectorPlan]")
        print(f"    item_selector: {self.item_selector}")
        print("    field_selectors:")
        for field, selectors in self.field_selectors.items():
            print(f" {field}: {selectors}")

class SelectorPlanner: 
    def __init__(self, html: str, collection_name: Optional[str], expected_fields: Dict[str, str]):
        self.html = html
        self.collection_name = collection_name
        self.expected_fields = expected_fields
        self.soup = BeautifulSoup(self.html, "lxml")

    def build_plan(self) -> SelectorPlan:
        item_selector = self._find_reapeated_item_selector()

        field_selectors: Dict[str, List[str]] = {}
        for field_name in self.expected_fields.keys():
            finds = self._find_field_selectors(field_name=field_name)
            field_selectors[field_name] = finds
        
        return SelectorPlan(item_selector=item_selector, field_selectors=field_selectors)
    
    def _find_reapeated_item_selector(self) -> Optional[str]:
        keywords = ["product", "card", "item", "listing", "result"]
        candidates = []

        for div in self.soup.select("div"):
            class_list = div.get("class", [])
            if not class_list:
                continue

            joined = " ".join(class_list).lower()

            if any(kw in joined for kw in keywords):
                candidates.append("." + ".".join(class_list))
        
        if candidates:
            from collections import Counter
            common = Counter(candidates).most_common(1)[0][0]
            return common
        
        return None
    
    def _find_field_selectors(self, field_name: str) -> List[str]:
        last_segment = field_name.split(".")[-1].lower()
        finds: List[str] = []

        finds.append(f"[data-testid*='{last_segment}']")
        finds.append(f"[data-{last_segment}]")
        finds.append(f"[aria-label*='{last_segment}']")

        finds.append(f".{last_segment}")
        finds.append(f".{last_segment}-value")
        finds.append(f".{last_segment}-text")
        finds.append(f".{last_segment}-label")
        finds.append(f".{last_segment}-name")
        finds.append(f".{last_segment}-field")

        if "price" in last_segment:
            finds.extend([
                ".price",
                ".product-price",
                "[data-price]",
                "[itemprop='price']",
            ])
        
        if "name" in last_segment or "title" in last_segment:
            finds.extend([
                ".product-name",
                ".product-title",
                "h1",
                "h2",
                "h3",
            ])
        
        if "description" in last_segment or "desc" in last_segment:
            finds.extend([
                ".description",
                ".product-description",
                "[itemprop='description']",
            ])
        
        if "image" in last_segment:
            finds.extend([
                "img.product-image",
                "img.main-image",
                "img[src]"
            ])
        
        if "availability" in last_segment or "in_stock" in last_segment:
            finds.extend([
                ".availability",
                "[data-availability]",
                "[aria-label*='in stock']",
                "[aria-label*='available']",
            ])
        
        if "cpu" in last_segment:
            finds.extend([
                ".cpu",
                "[data-cpu]",
                "[aria-label*='cpu']",
            ])
        
        if "ram" in last_segment or "memory" in last_segment:
            finds.extend([
                ".ram",
                "[data-ram]",
                "[aria-label*='ram']",
                "[aria-label*='memory']",
            ])
        
        seen = set()
        deduped: List[str] = []
        for sel in finds:
            if sel not in seen:
                deduped.append(sel)
                seen.add(sel)
        
        return deduped