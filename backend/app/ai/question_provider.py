from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class QuestionGeneratorProvider(ABC):
    """Interface for AI-powered question generation providers."""

    @abstractmethod
    def generate_questions(
        self,
        class_level: int,
        subject: str,
        topic: str,
        language: str,
        difficulty: str,
        question_type: str,
        num_questions: int,
        marks_per_question: float,
        source_type: str = "TOPIC_ONLY",
        source_context: Optional[str] = None,
        exact_topic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate exactly the requested number of questions."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Return True when the provider is configured and available."""
        raise NotImplementedError