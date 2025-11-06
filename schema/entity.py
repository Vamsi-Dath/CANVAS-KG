from pydantic import BaseModel, Field
from typing import Optional, Dict

class Entity(BaseModel):
    idx: int
    name: str
    type: str
    confidence: float = Field(ge=0.0, le=1.0)
    description: Optional[str] = ""
    properties: Optional[Dict] = {}