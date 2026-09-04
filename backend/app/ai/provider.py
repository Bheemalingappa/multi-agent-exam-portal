import logging
from typing import Optional

from app.ai.question_provider import QuestionGeneratorProvider
from app.ai.bedrock_question_provider import (
    BedrockQuestionGeneratorProvider,
)
from app.ai.gemini_question_provider import (
    GeminiQuestionGeneratorProvider,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_question_generator_provider(
) -> Optional[QuestionGeneratorProvider]:

    provider = settings.AI_PROVIDER.lower().strip()

    if provider == "gemini":
        try:
            logger.info(
                "Initializing Gemini question generator..."
            )
            return GeminiQuestionGeneratorProvider()
        except Exception as exc:
            logger.warning(
                "Unable to initialize Gemini question generator: %s",
                exc,
            )
            return None

    if provider in {"bedrock", "llm"}:
        try:
            logger.info(
                "Initializing AWS Bedrock question generator..."
            )
            return BedrockQuestionGeneratorProvider()
        except Exception as exc:
            logger.warning(
                "Unable to initialize Bedrock question generator: %s",
                exc,
            )

    logger.info(
        "Question generator provider is not configured."
    )

    return None