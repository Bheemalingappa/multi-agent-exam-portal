import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class RealtimeEventSchema(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    attempt_id: Optional[str] = None
    submission_id: Optional[str] = None
    sequence_number: int = 1
    progress: Optional[int] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
