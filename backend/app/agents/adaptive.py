import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AdaptiveChallengeEngine:
    """
    Adaptive Challenge Engine selecting next-tier assessment challenges
    from predefined safe template library based on candidate performance metrics.
    """

    CHALLENGE_TEMPLATES = {
        "REMEDIAL": {
            "type": "BASIC_SYNTAX_AND_FUNCTIONS",
            "difficulty": "BEGINNER",
            "description": "Review basic syntax, return value specifications, and runtime error prevention."
        },
        "STANDARD": {
            "type": "INPUT_VALIDATION",
            "difficulty": "INTERMEDIATE",
            "description": "Practice robust input validation, boundary condition checks, and error handling."
        },
        "ADVANCED": {
            "type": "CONCURRENCY_AND_TIMEOUTS",
            "difficulty": "ADVANCED",
            "description": "Inject Concurrency Control, Thread-Safety, and Database Timeout Resiliency."
        },
        "EXPERT": {
            "type": "DISTRIBUTED_FAULT_TOLERANCE",
            "difficulty": "EXPERT",
            "description": "Inject Dynamic Distributed Rate Limiting, Circuit Breaking, and Fault Tolerance."
        }
    }

    @classmethod
    def evaluate_adaptive_recommendation(
        cls,
        final_score: float,
        functional_score: float,
        latency_ms: float
    ) -> Dict[str, Any]:
        if final_score >= 90.0:
            tier = "EXPERT"
        elif final_score >= 80.0:
            tier = "ADVANCED"
        elif final_score >= 50.0:
            tier = "STANDARD"
        else:
            tier = "REMEDIAL"

        template = cls.CHALLENGE_TEMPLATES[tier]
        recommendation_text = f"🎯 Adaptive Recommendation ({tier}): {template['description']}"

        return {
            "challenge_tier": tier,
            "recommended_challenge": template,
            "recommendation_text": recommendation_text
        }
