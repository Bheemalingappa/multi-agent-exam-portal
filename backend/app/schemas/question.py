from pydantic import BaseModel, Field
from typing import Optional, List, Any

class TestCaseCreateSchema(BaseModel):
    input_data: str
    expected_output: str
    is_hidden: bool = True
    weight: float = Field(default=1.0, gt=0.0)
    timeout_seconds: int = Field(default=2, gt=0)

class TestCaseUpdateSchema(BaseModel):
    input_data: Optional[str] = None
    expected_output: Optional[str] = None
    is_hidden: Optional[bool] = None
    weight: Optional[float] = Field(default=None, gt=0.0)
    timeout_seconds: Optional[int] = Field(default=None, gt=0)

class TestCaseRecruiterResponseSchema(BaseModel):
    id: str
    question_id: str
    test_case_order: int
    input_data: str
    expected_output: str
    is_hidden: bool
    weight: float
    timeout_seconds: int

class QuestionCreateSchema(BaseModel):
    title: str
    description: str
    difficulty: str = "intermediate"
    language: str = "python"
    time_limit_seconds: int = Field(default=2, gt=0)
    memory_limit_mb: int = Field(default=128, gt=0)
    max_score: float = Field(default=100.0, ge=0.0, le=100.0)
    question_order: int = Field(default=1, gt=0)

class QuestionUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    language: Optional[str] = None
    time_limit_seconds: Optional[int] = Field(default=None, gt=0)
    memory_limit_mb: Optional[int] = Field(default=None, gt=0)
    max_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    question_order: Optional[int] = Field(default=None, gt=0)

class CandidateQuestionResponseSchema(BaseModel):
    """Candidate-safe Question response hiding expected outputs and hidden test case details."""
    id: str
    exam_id: str
    title: str
    description: str
    difficulty: str
    language: str
    time_limit_seconds: int
    memory_limit_mb: int
    max_score: float
    question_order: int

class RecruiterQuestionResponseSchema(BaseModel):
    id: str
    exam_id: str
    title: str
    description: str
    difficulty: str
    language: str
    time_limit_seconds: int
    memory_limit_mb: int
    max_score: float
    question_order: int
    is_active: bool
    created_at: Any
