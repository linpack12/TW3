from typing import Any, Optional
from pydantic import BaseModel, Field, HttpUrl

class Interaction(BaseModel):
    type: str
    selector: Optional[str] = None
    duration: Optional[int] = None
    direction: Optional[str] = None

class Options(BaseModel):
    pagination: bool = False
    max_pages: int = 1
    retry_failed: bool = True

class ScrapeConfig(BaseModel):
    url: HttpUrl = Field(..., description="Start URL to visit")
    schema: dict[str, Any]
    interactions: list[Interaction] = Field(default_factory=list)
    options: Options = Field(default_factory=Options)