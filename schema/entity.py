from pydantic import BaseModel, Field
from typing import Optional, Dict, Literal
from datetime import datetime

class Entity(BaseModel):
    idx: int
    name: str
    category: Literal["Person", "Event", "Artifact", "Concept"]
    type: str
    valid_start_time: datetime = datetime.now()
    valid_end_time: datetime = datetime(2099, 12, 31, 23, 59, 59)
    confidence: float = Field(ge=0.0, le=1.0)
    description: Optional[str] = ""
    properties: Optional[Dict] = {}