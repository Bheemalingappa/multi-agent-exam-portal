import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.database.models import AIUsageFact

logger = logging.getLogger(__name__)

# Gemini 1.5 Pro pricing estimate ($3.50 / 1M input tokens, $10.50 / 1M output tokens)
INPUT_TOKEN_RATE = 0.0000035
OUTPUT_TOKEN_RATE = 0.0000105

class AICostTracker:
    """Tracks token usage and calculates estimated API costs per evaluation task."""

    @staticmethod
    def record_usage(
        db: Session,
        submission_id: str,
        agent_name: str,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        status: str = "SUCCESS"
    ):
        try:
            total_tokens = input_tokens + output_tokens
            cost = (input_tokens * INPUT_TOKEN_RATE) + (output_tokens * OUTPUT_TOKEN_RATE)
            record = AIUsageFact(
                submission_id=submission_id,
                agent_name=agent_name,
                provider=provider,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                latency_ms=latency_ms,
                estimated_cost=round(cost, 6),
                status=status
            )
            db.add(record)
            db.commit()
            logger.info(f"Recorded AI Usage for submission '{submission_id}': {total_tokens} tokens (${cost:.6f})")
        except Exception as err:
            logger.warning(f"Failed recording AI cost tracking usage: {err}")
            db.rollback()
