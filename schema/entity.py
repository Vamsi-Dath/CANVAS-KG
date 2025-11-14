from pydantic import BaseModel, Field
from typing import Optional, Dict, Literal

class Entity(BaseModel):
    idx: int
    name: str
    category: Literal["Person", "Event", "Artifact", "Concept"]
    type: str
    confidence: float = Field(ge=0.0, le=1.0)
    description: Optional[str] = ""
    properties: Optional[Dict] = {}