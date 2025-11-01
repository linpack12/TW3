from src.agent.config_models import ScrapeConfig

sample_input = {
    "url": "https://example.com/products",
    "schema": {
        "products": [
            {
                "name": "string",
                "price": "number",
                "description": "string",
                "image_url": "string",
                "availability": "boolean",
                "specifications": {
                    "cpu": "string",
                    "ram": "string"
                }
            }
        ],
        "metadata": {
            "extraction_date": "datetime",
            "num_results": "number"
        }
    },
    "interactions": [
        {"type": "click", "selector": "#accept-cookies"},
        {"type": "wait", "duration": 2000},
        {"type": "scroll", "direction": "bottom"}
    ],
    "options": {
        "pagination": True,
        "max_pages": 5,
        "retry_failed": True
    }
}

config = ScrapeConfig(**sample_input)

print("URL:", config.url)
print("Interactions:", [i.type for i in config.interactions])
print("Want pagination?", config.options.pagination)
print("Schema keys:", list(config.schema.keys()))