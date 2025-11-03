from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from datetime import datetime
import re 

def _assign_nested(target: Dict[str, Any], dotted_key: str, value: Any) -> None:
    parts = dotted_key.split(".")
    cur = target
    
    # create nested structure
    for i, part in enumerate(parts):
        is_last = (i == len(parts) - 1)
        
        if is_last:
            cur[part] = value
        else:
            if part not in cur:
                cur[part] = {}
            elif not isinstance(cur[part], dict):
                cur[part] = {}
            
            cur = cur[part]

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
        # extract first number including decimals
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
        

class Extractor:
    def __init__(self, html: str, selector_plan, field_types: Dict[str, str]):
        self.soup = BeautifulSoup(html, "lxml")
        self.plan = selector_plan
        self.field_types = field_types
    
    def run(self) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        if self.plan.item_selector: 
            containers = self.soup.select(self.plan.item_selector)
        else:
            containers = [self.soup]
        
        all_items: List[Dict[str, Any]] = []
        missing_items: List[List[str]] = []

        for container in containers:
            item_data: Dict[str, Any] = {}
            missing_fields: List[str] = []

            for field_name, selector_candidates in self.plan.field_selectors.items(): 
                expected_type = self.field_types.get(field_name, "string")
                raw_val: Optional[str] = self._extract_first_match(container, selector_candidates)
                
                if raw_val is None:
                    missing_fields.append(field_name)
                    continue

                casted_val = _cast_value(raw_val, expected_type)
                if casted_val is None:
                    missing_fields.append(field_name)
                    continue

                _assign_nested(item_data, field_name, casted_val)
            
            if item_data:
                all_items.append(item_data)
                missing_items.append(missing_fields)
        
        quality_info = {
            "total_items": len(all_items),
            "missing_items": missing_items,
        }
        
        return all_items, quality_info
    
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
                continue
        
        return None