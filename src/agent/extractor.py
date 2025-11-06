from __future__ import annotations
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import re 

# Assigns a value into a nested dictionary structure given a dottet key
def _assign_nested(target: Dict[str, Any], dotted_key: str, value: Any) -> None:
    parts = dotted_key.split(".")
    cur = target
    
    # create nested structure
    for i, part in enumerate(parts):
        is_last = (i == len(parts) - 1)
        
        if is_last:
            cur[part] = value
        else:
            # Create intermediate dicts if missing or not of dict type
            if part not in cur or not isinstance(cur[part], dict):
                cur[part] = {}
            
            cur = cur[part]

"""
Attempts to cast a raw string into the expected data type defined 
by the craping schema (string, number, boolean, datetime).
"""
def _cast_value(raw_text: str, expected_type: str) -> Any:
    if raw_text is None:
        return None
    
    text = raw_text.strip()
    if not text:
        return None
    
    t = expected_type.lower()

    if t == "string":
        return text
    
    if t == "number":
        # extract first number including decimals and commas
        match = re.search(r"[0-9]+(?:[.,][0-9]+)?", text)
        if not match:
            return None
        num_txt = match.group(0).replace(",", ".")
        try:
            float_val = float(num_txt)
            if float_val.is_integer():
                return int(float_val)
            return float(num_txt)
        except ValueError: 
            return None
    
    # Boolean casting based on common textual patterns
    if t == "boolean":
        lowered = text.lower()
        truthy = ["in stock", "available", "yes", "true", "1", "instock"]
        falsy  = ["out of stock", "unavailable", "no", "false", "0"]
        if any(word in lowered for word in truthy):
            return True
        if any(word in lowered for word in falsy):
            return False
        return None
    
    if t == "datetime":
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            return parsed.isoformat()
        except ValueError:
            return None
    
    return text

# Extract the most relevant textual or attribute value from a given element
def _extract_candidate_value(el) -> str:
    if el is None:
        return None
    
    if el.name == "img" and el.has_attr("src"):
        src = el["src"].strip()
        return src if src else None
    if el.name == "a" and el.has_attr("href"):
        href = el["href"].strip()
        return href if href else None
    
    text = el.get_text(separator=" ", strip=True)
    return text if text else None
        
# Generic data extractor that converts HTML and a selector plan into structured data
class Extractor:
    def __init__(self, html: str, selector_plan, field_types: Dict[str, str]):
        # Parse the HTML into a DOM tree for CSS selector access
        self.soup = BeautifulSoup(html, "lxml")
        self.plan = selector_plan
        self.field_types = field_types
    
    """
    Executes the extraction plan and returns:
    - all_items -> list of structured records extracted from the HTML
    - quality_info -> diagnostic info about missing fields per item
    """
    def run(self) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        # Determine extraction scope: multiple containers or full page
        if self.plan.item_selector: 
            containers = self.soup.select(self.plan.item_selector)
        else:
            containers = [self.soup]
        
        all_items: List[Dict[str, Any]] = []
        missing_items: List[List[str]] = []

        # Process each container
        for container in containers:
            item_data: Dict[str, Any] = {}
            missing_fields: List[str] = []

            # Iterate over all target fields and their candidate selectors
            for field_name, selector_candidates in self.plan.field_selectors.items(): 
                expected_type = self.field_types.get(field_name, "string")

                # Try each selector in order until one matches
                raw_val: Optional[str] = self._extract_first_match(container, selector_candidates)
                
                if raw_val is None:
                    missing_fields.append(field_name)
                    continue

                casted_val = _cast_value(raw_val, expected_type)
                if casted_val is None:
                    missing_fields.append(field_name)
                    continue

                _assign_nested(item_data, field_name, casted_val)
            
            # Only include non empty results
            if item_data:
                all_items.append(item_data)
                missing_items.append(missing_fields)
        
        quality_info = {
            "total_items": len(all_items),
            "missing_items": missing_items,
        }
        
        return all_items, quality_info
    
    """
    Attemps each CSS selector in order and return first non empty value
    """
    def _extract_first_match(self, scope, selector_candidates: List[str]) -> Optional[str]:
        for sel in selector_candidates: 
            try:
                el = scope.select_one(sel)
                if not el:
                    continue

                extracted = _extract_candidate_value(el)
                if extracted:
                    return extracted
            except Exception:
                # Skip broken selectors or parsing errors
                continue
        
        return None