from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class QuestionResultSchema(BaseModel):
    question_id: str
    number: int
    question: str
    question_type: str = "MCQ"
    user_answer: Optional[str] = None
    awarded_marks: float = 0.0
    maximum_marks: float = 10.0
    correctness: str = "INCORRECT"  # CORRECT, PARTIAL, INCORRECT
    findings: List[str] = Field(default_factory=list)
    reasoning_summary: Optional[str] = None
    evaluator_agent: Optional[str] = "MULTI_AGENT_EVALUATOR"

class ExamEvaluationResponseSchema(BaseModel):
    id: str
    attempt_id: str
    exam_id: str
    candidate_id: str
    status: str  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    total_score: float
    maximum_score: float
    percentage: float
    grade: str
    question_results: List[Dict[str, Any]] = Field(default_factory=list)
    evaluator_metadata: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class StudentEvaluationSummarySchema(BaseModel):
    attempt_id: str
    exam_id: str
    title: str
    class_level: Optional[int] = None
    subject: Optional[str] = None
    status: str
    total_score: float
    maximum_score: float
    percentage: float
    grade: str
    completed_at: Optional[datetime] = None
    total_questions: int = 0
    answered_questions: int = 0

class EvaluationRetryRequestSchema(BaseModel):
    force_recalculate: bool = False
