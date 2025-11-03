from typing import Any, Dict, List, Optional
from datetime import datetime
import json

class ResultFormatter: 
    def __init__(self, collection_name: str, expected_fields: Dict[str, str]):
        self.collection_name = collection_name
        self.expected_fields = expected_fields

    def format_success(self, items: List[Dict[str, Any]], metadata: Dict[str, Any], missing_items: List[List[str]]) -> Dict[str, Any]:
        quality_report = self._generate_quality_report(items, missing_items)

        data = {
            self.collection_name: items, 
            "metadata": metadata
        }
        
        return {
            "status": "success",
            "data": data,
            "quality_report": quality_report
        }

    def format_error(self, error_message: str, error_details: Optional[str] = None) -> Dict[str, Any]:
        return {
            "status": "error",
            "error": error_message,
            "details": error_details,
            "data": None,
            "quality_report": None
        }

    def _generate_quality_report(self, items: List[Dict[str, Any]], missing_items: List[List[str]]) -> Dict[str, Any]:
        total_items = len(items)

        if total_items == 0: 
            return {
                "total_items": 0,
                "complete_items": 0,
                "completion_rate": 0.0,
                "missing_fields_summary": [],
                "errors": []
            }
        
        while len(missing_items) < total_items:
            missing_items.append([])
        #count complete items 
        complete_items = sum(1 for missing in missing_items[:total_items] if len(missing) == 0)
        completion_rate = complete_items / total_items if total_items > 0 else 0.0

        #aggregate missing fields
        missing_fields_summary = self._aggregate_missing_fields(missing_items)

        return {
            "total_items": total_items,
            "complete_items": complete_items,
            "completion_rate": round(completion_rate, 3),
            "missing_fields_summary": missing_fields_summary,
            "errors": []
        }
    
    def _aggregate_missing_fields(self, missing_items: List[List[str]]) -> List[str]:
        from collections import Counter 

        all_missing = []
        for missing_list in missing_items:
            all_missing.extend(missing_list)
        
        if not all_missing:
            return []
        
        counts = Counter(all_missing)
        result = []
        for field, count in counts.most_common():
            result.append(f"{field}: {count} items")
        
        return result
    
    def save_to_file(self, result: Dict[str, Any], file_path: str) -> None:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    def to_json(self, result: Dict[str, Any]) -> str:
        return json.dumps(result, indent=2, ensure_ascii=False)