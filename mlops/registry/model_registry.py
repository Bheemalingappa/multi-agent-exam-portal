from typing import List, Dict, Any

class ModelRegistry:
    """
    MLOps Model & Prompt Version Registry tracking evaluation models
    across lifecycle states (EXPERIMENTAL, VALIDATED, STAGING, PRODUCTION, DEPRECATED).
    """

    MODELS = [
        {
            "model_id": "mdl_gemini_15_pro_v1",
            "provider": "gemini",
            "model_name": "gemini-1.5-pro",
            "version": "1.0.0",
            "prompt_version": "v2.1",
            "status": "PRODUCTION",
            "evaluation_score": 94.5
        },
        {
            "model_id": "mdl_deterministic_fallback_v1",
            "provider": "deterministic",
            "model_name": "ast-rule-engine",
            "version": "1.0.0",
            "prompt_version": "v1.0",
            "status": "PRODUCTION",
            "evaluation_score": 88.0
        }
    ]

    @classmethod
    def list_registered_models(cls) -> List[Dict[str, Any]]:
        return cls.MODELS
