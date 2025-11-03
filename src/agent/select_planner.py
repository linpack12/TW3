from __future__ import annotations
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from collections import Counter

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
        keywords = ["product", "card", "item", "listing", "result", "post", "entry", "record"]
        candidates = []

        for div in self.soup.select("div[data-testid], div[data-id]"):
            classes = div.get("class", [])
            data_testid = div.get("data-testid", "")

            if classes or data_testid:
                sel = self._element_to_selector(div)
                if sel:
                    candidates.append(sel)
        
        for div in self.soup.select("div[class]"):
            class_list = div.get("class", [])
            if not class_list:
                continue

            joined = " ".join(class_list).lower()

            if any(kw in joined for kw in keywords):
                sel = self._element_to_selector(div)
                if sel:
                    candidates.append(sel)
        
        for el in self.soup.select("li[class], article[class], section.item, div.item"):
            sel = self._element_to_selector(el)
            if sel:
                candidates.append(sel)
        
        if candidates:
            counts = Counter(candidates)
            most_common = Counter(candidates).most_common(1)[0][0]
            return most_common
        
        return None
    
    def _element_to_selector(self, el) -> Optional[str]:
        if el.has_attr("data-testid"):
            return f"[data-testid='{el['data-testid']}']"

        if el.has_attr("data-id"):
            return f"[data-id='{el['data-id']}']"
        
        classes = el.get("class", [])
        if classes:
            return "." + ".".join(classes)
        
        if el.has_attr("id"):
            return f"#{el['id']}"
        
        return None
    
    def _find_field_selectors(self, field_name: str) -> List[str]:
        last_segment = field_name.split(".")[-1].lower()
        finds: List[str] = []

        #Data attributes - Tier 1 most robust 
        finds.append(f"[data-testid*='{last_segment}']")
        finds.append(f"[data-testid*='{last_segment.replace('_', '-')}']")
        finds.append(f"[data-{last_segment}]")
        finds.append(f"[data-{last_segment.replace('_', '-')}]")

        #Aria attributes 
        finds.append(f"[aria-label*='{last_segment}']")
        finds.append(f"[aria-label*='{last_segment.replace('_', ' ')}']")
        finds.append(f"[role*='{last_segment}']")

        #Microdata semantic
        finds.append(f"[itemprop='{last_segment}']")

        #Class based selectors - Tier 2 robustness
        finds.append(f".{last_segment}")
        finds.append(f".{last_segment.replace('_', '-')}")
        finds.append(f".{last_segment}-value")
        finds.append(f".{last_segment}-text")
        finds.append(f".{last_segment}-label")
        finds.append(f".{last_segment}-name")
        finds.append(f".{last_segment}-field")

        #Domain specific selectors - Tier 3
        if "price" in last_segment or "cost" in last_segment:
            finds.extend([
                ".price",
                ".product-price",
                ".price-value",
                "[data-price]",
                "[itemprop='price']",
                ".amount",
                ".cost"
            ])
        
        if "name" in last_segment or "title" in last_segment:
            finds.extend([
                ".product-name",
                ".product-title",
                ".name",
                ".title",
                "h1",
                "h2",
                "h3",
                "[itemprop='name']"
            ])
        
        if "description" in last_segment or "desc" in last_segment:
            finds.extend([
                ".description",
                ".product-description",
                ".desc",
                ".summary",
                "p.description",
                "[itemprop='description']"
            ])
        
        if "image" in last_segment or "photo" in last_segment or "picture" in last_segment:
            finds.extend([
                "img.product-image",
                "img.main-image",
                "img[src]",
                "img[alt*='product']",
                ".image img",
                ".photo img",
                "[itemprop='image']"
            ])
        
        if "availability" in last_segment or "in_stock" in last_segment or "stock" in last_segment:
            finds.extend([
                ".availability",
                ".stock",
                ".in-stock",
                "[data-availability]",
                "[data-stock]",
                "[aria-label*='stock']",
                "[aria-label*='available']"
            ])
        
        if "cpu" in last_segment or "processor" in last_segment:
            finds.extend([
                ".cpu",
                ".processor",
                "[data-cpu]",
                "[aria-label*='cpu']",
                "[aria-label*='processor']"
            ])
        
        if "ram" in last_segment or "memory" in last_segment:
            finds.extend([
                ".ram",
                ".memory",
                "[data-ram]",
                "[data-memory]",
                "[aria-label*='ram']",
                "[aria-label*='memory']"
            ])
        
        seen = set()
        deduped: List[str] = []
        for sel in finds:
            if sel not in seen:
                deduped.append(sel)
                seen.add(sel)
        
        return deduped