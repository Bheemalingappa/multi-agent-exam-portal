from pydantic import BaseModel
from typing import Optional, Dict, Any

class AttemptStartSchema(BaseModel):
    exam_id: str

class AnswerSaveSchema(BaseModel):
    answers: Dict[str, Any]

class AttemptResponseSchema(BaseModel):
    id: str
    candidate_id: str
    exam_id: str
    status: str
    started_at: Any
    expires_at: Any
    remaining_seconds: int
    submitted_at: Optional[Any] = None
    completed_at: Optional[Any] = None
    answers: Optional[Dict[str, Any]] = None
    total_score: float
    max_score: float
