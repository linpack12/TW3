from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

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