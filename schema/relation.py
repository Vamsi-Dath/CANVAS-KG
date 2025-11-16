from pydantic import BaseModel, Field
from typing import Optional, Dict, Literal
from datetime import datetime

class Relation(BaseModel):
    id: int
    type: Literal['relation']
    subject_entity_id: int
    predicate: str = "related_to"
    object_entity_id: int
    valid_start_time: datetime = datetime.now()
    valid_end_time: datetime = datetime(2099, 12, 31, 23, 59, 59)
    confidence: float = Field(ge=0.0, le=1.0)
    description: Optional[str] = ""
    properties: Optional[Dict] = {}