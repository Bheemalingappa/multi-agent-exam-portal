from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator

class EvaluationRequest(BaseModel):
    agent_type: str
    submitted_code: str
    exam_title: str
    execution_metrics: Dict[str, Any] = Field(default_factory=dict)
    functional_score: float = 100.0

class AgentEvidenceItem(BaseModel):
    category: str
    description: str
    severity: str = "INFO"

class EvaluationResponse(BaseModel):
    agent_type: str
    score: float = Field(ge=0.0, le=100.0)
    confidence: float = Field(ge=0.0, le=1.0, default=0.95)
    risk_level: str = "LOW"
    findings: List[str] = Field(default_factory=list)
    reasoning_summary: str
    evidence: List[AgentEvidenceItem] = Field(default_factory=list)
    latency_ms: float = 0.0

    @field_validator("score", mode="before")
    @classmethod
    def clamp_score(cls, v: Any) -> float:
        try:
            val = float(v)
            return max(0.0, min(100.0, val))
        except (ValueError, TypeError):
            return 50.0

    @field_validator("confidence", mode="before")
    @classmethod
    def clamp_confidence(cls, v: Any) -> float:
        try:
            val = float(v)
            return max(0.0, min(1.0, val))
        except (ValueError, TypeError):
            return 0.90
