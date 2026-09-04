from pydantic import BaseModel, Field
from typing import Optional, Any

class ExamCreateSchema(BaseModel):
    title: str
    description: str
    class_level: int = Field(default=10, ge=1, le=12)
    subject: str = Field(default="Mathematics")
    language: str = Field(default="English")
    difficulty: str = "intermediate"
    duration_minutes: int = Field(default=60, gt=0)
    max_score: float = Field(default=100.0, gt=0.0, le=100.0)
    max_attempts: int = Field(default=1, gt=0)

class ExamUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    class_level: Optional[int] = Field(default=None, ge=1, le=12)
    subject: Optional[str] = None
    language: Optional[str] = None
    difficulty: Optional[str] = None
    duration_minutes: Optional[int] = Field(default=None, gt=0)
    max_score: Optional[float] = Field(default=None, gt=0.0, le=100.0)
    max_attempts: Optional[int] = Field(default=None, gt=0)
    is_active: Optional[bool] = None

class ExamResponseSchema(BaseModel):
    id: str
    title: str
    description: str
    class_level: int = 10
    subject: str = "Mathematics"
    language: str = "English"
    difficulty: str
    duration_minutes: int
    max_score: float
    max_attempts: int
    is_active: bool
    is_published: bool
    created_at: Any
