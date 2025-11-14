from pydantic import BaseModel, Field
from typing import Optional, Dict, Literal

class Relation(BaseModel):
    id: int
    type: Literal['relation']
    subject_entity_id: int
    predicate: str = "related_to"
    object_entity_id: int
    confidence: float = Field(ge=0.0, le=1.0)
    description: Optional[str] = ""
    properties: Optional[Dict] = {}