import logging
from typing import Dict, Any
from app.agents.provider import get_agent_provider

logger = logging.getLogger(__name__)

class SecurityAgent:
    """
    Security Agent evaluating code for vulnerability patterns:
    - Injection risks
    - Hardcoded secrets
    - Unsafe file system manipulation
    - Container escape / AST violation flags
    """

    @staticmethod
    def evaluate_security(
        submitted_code: str,
        exam_title: str,
        execution_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        logger.info("Security Agent running vulnerability analysis...")

        provider = get_agent_provider()
        res = provider.evaluate("SECURITY", submitted_code, exam_title, execution_metrics)

        # Additional deterministic security rules
        findings = list(res.get("findings", []))
        risk_level = res.get("risk_level", "LOW")
        score = float(res.get("score", 100.0))

        # Check hardcoded secret keywords
        secret_keywords = ["password =", "api_key =", "secret =", "private_key ="]
        for kw in secret_keywords:
            if kw in submitted_code.lower():
                findings.append(f"Security Alert: Hardcoded credentials keyword '{kw.split('=')[0].strip()}' detected in source code.")
                risk_level = "MEDIUM"
                score = min(score, 70.0)

        return {
            "agent_type": "SECURITY",
            "score": round(score, 2),
            "confidence": res.get("confidence", 0.95),
            "risk_level": risk_level,
            "findings": findings,
            "reasoning_summary": res.get("reasoning_summary", "Security Analysis Complete.")
        }
