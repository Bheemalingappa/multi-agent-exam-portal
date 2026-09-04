import logging
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session

from app.database.models import SubmissionFact, AgentEvaluation, AgentConsensus
from app.agents.provider import get_agent_provider
from app.agents.security import SecurityAgent
from app.core.config import settings

logger = logging.getLogger(__name__)

class A2AConsensusEngine:
    """
    Decoupled Agent-to-Agent (A2A) consensus engine.
    Orchestrates negotiation rounds between Mentor, QA, and Security Agents up to MAX_A2A_ROUNDS.
    Persists evaluation traces into fact_agent_evaluations and fact_agent_consensus.
    """

    @classmethod
    def run_consensus(
        cls,
        db: Session,
        submission: SubmissionFact,
        submitted_code: str,
        exam_title: str,
        execution_metrics: Dict[str, Any],
        functional_score: float
    ) -> Dict[str, Any]:
        logger.info(f"Running A2A Consensus Engine for submission '{submission.submission_id}'...")

        provider = get_agent_provider()
        max_rounds = settings.MAX_A2A_ROUNDS

        mentor_res = provider.evaluate("MENTOR", submitted_code, exam_title, execution_metrics)
        qa_res = provider.evaluate("QA", submitted_code, exam_title, execution_metrics)
        sec_res = SecurityAgent.evaluate_security(submitted_code, exam_title, execution_metrics)

        # Store individual agent evaluations in PostgreSQL fact_agent_evaluations
        for agent_data in [mentor_res, qa_res, sec_res]:
            eval_record = AgentEvaluation(
                submission_id=submission.submission_id,
                agent_type=agent_data["agent_type"],
                round_number=1,
                score=agent_data["score"],
                confidence=agent_data.get("confidence", 0.95),
                risk_level=agent_data.get("risk_level", "LOW"),
                findings=agent_data.get("findings", []),
                reasoning_summary=agent_data.get("reasoning_summary", ""),
                latency_ms=agent_data.get("latency_ms", 0.0)
            )
            db.add(eval_record)

        mentor_score = float(mentor_res["score"])
        qa_score = float(qa_res["score"])
        sec_score = float(sec_res["score"])

        score_variance = abs(mentor_score - qa_score)
        round_count = 1

        # Negotiation rounds loop if score variance is high (> 20 pts)
        while score_variance > 20.0 and round_count < max_rounds:
            round_count += 1
            logger.info(f"A2A Negotiation Round {round_count}: Reconciling Mentor ({mentor_score}) vs QA ({qa_score})...")
            # Reconcile scores towards weighted midpoint
            midpoint = (mentor_score + qa_score) / 2.0
            mentor_score = round((mentor_score * 0.7) + (midpoint * 0.3), 2)
            qa_score = round((qa_score * 0.7) + (midpoint * 0.3), 2)
            score_variance = abs(mentor_score - qa_score)

        # Weighted Final Score Calculation
        code_quality_score = (mentor_score + qa_score) / 2.0
        latency = execution_metrics.get("execution_latency_ms", 0.0)
        efficiency_score = 100.0 if latency < 500 else (80.0 if latency < 1500 else 50.0)
        security_score = sec_score
        exit_code = execution_metrics.get("exit_code", 0)
        error_handling_score = 100.0 if exit_code == 0 else 40.0
        testing_quality_score = functional_score

        final_consensus_score = round(
            (functional_score * 0.40) +
            (code_quality_score * 0.20) +
            (efficiency_score * 0.15) +
            (security_score * 0.10) +
            (error_handling_score * 0.10) +
            (testing_quality_score * 0.05),
            2
        )

        confidence = round(max(0.70, 1.0 - (score_variance / 200.0)), 2)

        # Persist fact_agent_consensus record
        consensus_record = AgentConsensus(
            submission_id=submission.submission_id,
            round_count=round_count,
            mentor_score=mentor_score,
            qa_score=qa_score,
            security_score=sec_score,
            consensus_score=final_consensus_score,
            confidence=confidence,
            consensus_method="WEIGHTED_MULTI_AGENT_CONSENSUS",
            disagreement_summary=f"Score variance {score_variance} pts resolved after {round_count} negotiation rounds."
        )
        db.add(consensus_record)
        db.commit()

        return {
            "mentor_score": mentor_score,
            "qa_score": qa_score,
            "security_score": sec_score,
            "consensus_score": final_consensus_score,
            "confidence": confidence,
            "round_count": round_count,
            "mentor_res": mentor_res,
            "qa_res": qa_res,
            "sec_res": sec_res
        }
