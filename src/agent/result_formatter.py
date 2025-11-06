from typing import Any, Dict, List, Optional
import json

# Formats extraction results and builds a quality report 
class ResultFormatter: 
    def __init__(self, collection_name: str, expected_fields: Dict[str, str]):
        self.collection_name = collection_name
        self.expected_fields = expected_fields

    # Return a unified success response with data and quality metrics
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

    # Return a unified error response structure
    def format_error(self, error_message: str, error_details: Optional[str] = None) -> Dict[str, Any]:
        return {
            "status": "error",
            "error": error_message,
            "details": error_details,
            "data": None,
            "quality_report": None
        }

    # Compute summary stats -> totals, completion rate, missing field counts
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
        
        # Align list lengths 
        while len(missing_items) < total_items:
            missing_items.append([])

        # Count complete items 
        complete_items = sum(1 for missing in missing_items[:total_items] if len(missing) == 0)
        # Calcultae completion rate
        completion_rate = complete_items / total_items if total_items > 0 else 0.0

        # Aggregate missing fields
        missing_fields_summary = self._aggregate_missing_fields(missing_items)

        return {
            "total_items": total_items,
            "complete_items": complete_items,
            "completion_rate": round(completion_rate, 3),
            "missing_fields_summary": missing_fields_summary,
            "errors": []
        }
    
    # Count how often each field was missing and return sorted summary strings
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
    
    # Write formatted result to disk as JSON 
    def save_to_file(self, result: Dict[str, Any], file_path: str) -> None:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    # Return result as JSON string - same format as save_to_file
    def to_json(self, result: Dict[str, Any]) -> str:
        return json.dumps(result, indent=2, ensure_ascii=False)