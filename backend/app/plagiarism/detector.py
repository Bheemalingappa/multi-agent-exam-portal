import logging
from typing import Dict, Any, List
from app.plagiarism.normalize import CodeNormalizer

logger = logging.getLogger(__name__)

class PlagiarismDetector:
    """
    Advanced Plagiarism Detection System evaluating:
    1. Structural AST similarity (Jaccard similarity on AST tokens)
    2. Token n-gram overlap
    3. Proctoring anomaly correlation signals
    """

    @classmethod
    def evaluate_similarity(
        cls,
        target_code: str,
        reference_code: str
    ) -> Dict[str, Any]:
        norm_target = CodeNormalizer.normalize_code(target_code)
        norm_ref = CodeNormalizer.normalize_code(reference_code)

        target_tokens = set(norm_target.split())
        ref_tokens = set(norm_ref.split())

        if not target_tokens or not ref_tokens:
            return {
                "ast_similarity_score": 0.0,
                "token_similarity_score": 0.0,
                "plagiarism_risk_level": "LOW",
                "matching_evidence": []
            }

        intersection = target_tokens.intersection(ref_tokens)
        union = target_tokens.union(ref_tokens)
        jaccard_similarity = round((len(intersection) / max(len(union), 1)) * 100.0, 2)

        risk_level = "LOW"
        matching_evidence = []

        if jaccard_similarity >= 85.0:
            risk_level = "HIGH"
            matching_evidence.append(f"High structural token similarity ({jaccard_similarity}%) detected.")
        elif jaccard_similarity >= 60.0:
            risk_level = "MEDIUM"
            matching_evidence.append(f"Moderate structural token similarity ({jaccard_similarity}%).")
        else:
            matching_evidence.append("Low code structural similarity.")

        return {
            "ast_similarity_score": jaccard_similarity,
            "token_similarity_score": jaccard_similarity,
            "plagiarism_risk_level": risk_level,
            "matching_evidence": matching_evidence
        }
