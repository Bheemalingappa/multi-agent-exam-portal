import logging
from app.core.config import settings
from app.agents.base import AgentProvider
from app.agents.fallback import DeterministicFallbackProvider

logger = logging.getLogger(__name__)

def get_agent_provider() -> AgentProvider:
    """
    Factory function returning active AgentProvider.
    Defaults to DeterministicFallbackProvider for production stability.
    """
    if settings.AI_PROVIDER.lower() == "llm" and settings.LLM_API_KEY:
        try:
            # Place for LLM API Provider Adapter integration (e.g. Gemini 1.5 Pro / Flash)
            logger.info("Initializing LLM Agent Provider...")
            return DeterministicFallbackProvider()
        except Exception as e:
            logger.warning(f"Failed initializing LLM provider ({e}); using Deterministic Fallback.")
            return DeterministicFallbackProvider()

    logger.info("Using Deterministic Fallback Agent Provider.")
    return DeterministicFallbackProvider()
