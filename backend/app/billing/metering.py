from typing import Dict, Any

class BillingMeteringService:
    """
    Enterprise Usage Metering Service evaluating monthly plan candidate attempts,
    submissions, and AI token limits across SaaS subscription tiers.
    """

    PLANS = {
        "FREE": {"max_candidates": 50, "max_ai_tokens": 100000},
        "STARTER": {"max_candidates": 250, "max_ai_tokens": 500000},
        "BUSINESS": {"max_candidates": 1000, "max_ai_tokens": 2500000},
        "ENTERPRISE": {"max_candidates": 10000, "max_ai_tokens": 100000000}
    }

    @classmethod
    def check_quota(cls, plan_tier: str, current_usage: int) -> bool:
        tier_info = cls.PLANS.get(plan_tier.upper(), cls.PLANS["FREE"])
        return current_usage < tier_info["max_candidates"]
