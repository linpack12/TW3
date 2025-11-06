from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

class InteractionType(str, Enum):
    CLICK = "click"
    SCROLL = "scroll"
    WAIT = "wait"
    EXTRACT = "extract"

class ScrollDirection(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"

# User interaction executed by the scraper 
class Interaction(BaseModel):
    type: InteractionType
    selector: Optional[str] = None
    duration: Optional[int] = Field(default=None, ge=0, description="Ms to wait (only requiered when type=wait)")
    direction: Optional[ScrollDirection] = None

    """
    Rules per interaction type:
    - scroll -> direction is required
    - wait -> duration is required >= 0
    - click/extract -> selector is required
    """
    @model_validator(mode="after")
    def check_required_fields(self):
        if self.type == InteractionType.SCROLL and self.direction is None:
            raise ValueError("direction is required when type='scroll'")
        if self.type == InteractionType.WAIT and self.duration is None: 
            raise ValueError("duration is required when type='wait'")
        if self.type in (InteractionType.CLICK, InteractionType.EXTRACT) and self.selector is None:
            raise ValueError(f"selector is required when type='{self.type.value}'")
        
        return self
        

# Runtime options for the scraping session
class Options(BaseModel):
    pagination: bool = False
    max_pages: int = 1
    retry_failed: bool = True

"""
Full config for a scraping job. 
- url -> start url 
- schema -> json schema describing extracted data
- interactions -> ordered steps (click/scroll/wait/extract)
- options: pagination, retries, etc
"""
class ScrapeConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    url: HttpUrl = Field(..., description="Start URL to visit")
    schema_: dict[str, Any] = Field(
        ...,
        alias="schema",
        description="JSON schema defining structure of data to extract"
    )
    interactions: list[Interaction] = Field(default_factory=list)
    options: Options = Field(default_factory=Options)
    
    @property
    def schema(self) -> dict[str, Any]:
        return self.schema_