from __future__ import annotations
from typing import Any

# Analyze a JSON schema to extraxt collection name and flattened field map
class SchemaAnalyser:

    def __init__(self, schema: dict[str, Any]):
        self.schema = schema
        self.collection_name: str | None = None # e.g. "products"
        self.item_fields: dict[str, str] = {} # e.g. {"title": "string"}
        self._analyze()

    # Detects the first list of dicts structure in the schema and treats it as the main collection
    def _analyze(self) -> None: 
        for key, value in self.schema.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                self.collection_name = key
                self.item_fields = self._flatten_fields(value[0])
                break # Stop at first valid collection
    
    # Recursively flattens nested dicts into dot notation
    def _flatten_fields(self, obj: dict[str, Any], prefix: str = "") -> dict[str, str]:
        out: dict[str, str] = {}
        for field_name, field_type in obj.items():
            full_key = f"{prefix}.{field_name}" if prefix else field_name 
            if isinstance(field_type, dict):
                # Recurse into nested  structures
                nested = self._flatten_fields(field_type, prefix=full_key)
                out.update(nested)
            else:
                out[full_key] = str(field_type)
        return out
    
    # Prints the detected collection and its expected fields - for debugging
    def debug_print(self) -> None:
        print("[SchemaAnalyzer] collection_name:", self.collection_name)
        print("[SchemaAnalyzer] expected fields:")
        for k, v in self.item_fields.items():
            print(f" - {k}: {v}")