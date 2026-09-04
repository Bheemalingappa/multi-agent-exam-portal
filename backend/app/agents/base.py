from abc import ABC, abstractmethod
from typing import Dict, Any

class AgentProvider(ABC):
    """Abstract base class interface for AI evaluation providers."""

    @abstractmethod
    def evaluate(
        self,
        agent_type: str,
        submitted_code: str,
        exam_title: str,
        execution_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Runs evaluation for a specific agent type and returns validated structured output."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Returns provider availability status."""
        pass
