import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any, Tuple, List
from celery import shared_task
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.database.models import SubmissionFact, Exam, Question, TestCase, SandboxProfile, ExamAttempt
from app.pipeline.sandbox import DockerSandboxEngine
from app.pipeline.test_runner import HiddenTestRunner
from app.agents.consensus import A2AConsensusEngine
from app.agents.adaptive import AdaptiveChallengeEngine
from app.realtime.redis_events import RedisEventPublisher
from app.core.config import settings

logger = logging.getLogger(__name__)

class MCPContextInjector:
    """Model Context Protocol (MCP) context injector with strict path traversal protection."""

    @staticmethod
    def sanitize_path(file_path: str) -> str:
        if ".." in file_path or file_path.startswith("/") or file_path.startswith("\\"):
            raise ValueError(f"Path Traversal Violation: Prohibited file path '{file_path}'")
        return file_path

    @classmethod
    def get_context(cls, exam: Exam, code: str) -> Tuple[Dict[str, Any], str]:
        sample_paths = ["solution.py", "config.json", "README.md"]
        for p in sample_paths:
            cls.sanitize_path(p)

        context_payload = {
            "protocol_version": "2024-11-05",
            "context_type": "repository_tree",
            "metadata": {
                "exam_id": str(exam.id),
                "exam_title": exam.title,
                "difficulty": exam.difficulty,
                "code_bytes": len(code)
            },
            "environment_tree": {
                "root": "candidate_workspace/",
                "files": [
                    {"path": "solution.py", "size_bytes": len(code)},
                    {"path": "config.json", "content": json.dumps({"difficulty": exam.difficulty})}
                ]
            }
        }

        raw_json = json.dumps(context_payload, sort_keys=True)
        context_hash = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()
        return context_payload, context_hash


class BehavioralAnomalyOracle:
    """Evaluates telemetry signals: typing cadence, focus loss, paste ratio."""

    @staticmethod
    def analyze(telemetry: Dict[str, Any], submitted_code: str) -> Dict[str, Any]:
        paste_events = telemetry.get("paste_events_count", len(telemetry.get("paste_events", [])))
        focus_lost_count = telemetry.get("focus_lost_count", len(telemetry.get("focus_events", [])))
        typing_speed_wpm = telemetry.get("typing_speed_wpm", 45.0)

        code_len = len(submitted_code)
        paste_ratio = round((paste_events * 100.0) / max(code_len, 1), 2)

        anomaly_score = 0.0
        signals = []

        if paste_events > 3 or paste_ratio > 35.0:
            anomaly_score += 0.45
            signals.append("High paste ratio payload detected relative to source code length.")

        if focus_lost_count > 4:
            anomaly_score += 0.35
            signals.append(f"Window focus lost {focus_lost_count} times during exam attempt.")

        if typing_speed_wpm > 180.0:
            anomaly_score += 0.20
            signals.append("Abnormal typing speed cadence detected (>180 WPM).")

        anomaly_score = min(round(anomaly_score, 2), 1.0)
        confidence = round(0.85 + (0.10 * (1.0 - anomaly_score)), 2)

        return {
            "anomaly_score": anomaly_score,
            "confidence": confidence,
            "paste_ratio": paste_ratio,
            "focus_loss_count": focus_lost_count,
            "typing_anomaly_score": min(round(typing_speed_wpm / 200.0, 2), 1.0),
            "signals": signals
        }


@shared_task(bind=True, name="app.pipeline.tasks.evaluate_submission_task", max_retries=2)
def evaluate_submission_task(self, submission_id: str) -> Dict[str, Any]:
    """
    12-Stage Evaluation Pipeline with Real-Time Events & Multi-Agent Consensus:
    QUEUED (0%) -> STATIC_ANALYSIS (10%) -> SANDBOX_RUNNING (20%) -> TEST_CASE_EXECUTION (35%) ->
    EXECUTION_COMPLETE (40%) -> MCP_CONTEXT (45%) -> ANOMALY_ANALYSIS (55%) ->
    SECURITY_ANALYSIS (80%) -> A2A_CONSENSUS (90%) -> ADAPTIVE_ANALYSIS (95%) -> FINALIZED (100%)
    """
    db: Session = SessionLocal()
    task_id = getattr(self.request, "id", f"task_{submission_id[:8]}")

    def notify_stage(stage_name: str, progress: int, attempt_id: str = None, extra_payload: dict = None):
        payload = {"stage": stage_name, "status": "RUNNING"}
        if extra_payload:
            payload.update(extra_payload)
        RedisEventPublisher.publish_event(
            event_type="EVALUATION_STAGE_CHANGED",
            attempt_id=attempt_id,
            submission_id=submission_id,
            progress=progress,
            payload=payload
        )

    try:
        submission = db.query(SubmissionFact).filter(SubmissionFact.submission_id == submission_id).first()
        if not submission:
            logger.error(f"Task {task_id}: Submission {submission_id} not found in DB.")
            return {"error": "Submission not found"}

        if submission.status in ["FINALIZED", "COMPLETED"]:
            return {"submission_id": submission_id, "status": submission.status}

        attempt_id_str = str(submission.attempt_id) if submission.attempt_id else None
        submission.started_at = datetime.utcnow()
        submission.celery_task_id = task_id

        # STAGE 1: STATIC_ANALYSIS (10%)
        submission.status = "STATIC_ANALYSIS"
        db.commit()
        notify_stage("STATIC_ANALYSIS", 10, attempt_id_str)

        sandbox_engine = DockerSandboxEngine(
            image_name=settings.SANDBOX_IMAGE,
            blocked_rules_path="sandbox/blocked_builtins.json"
        )

        try:
            sandbox_engine.ast_pre_screen(submission.source_code)
            submission.static_analysis_status = "PASSED"
            submission.security_risk_level = "LOW"
        except ValueError as ve:
            submission.static_analysis_status = "FAILED"
            submission.security_risk_level = "CRITICAL"
            submission.status = "SECURITY_BLOCKED"
            submission.error_message = str(ve)
            submission.completed_at = datetime.utcnow()
            db.commit()
            notify_stage("SECURITY_BLOCKED", 100, attempt_id_str, {"error": str(ve)})
            return {"submission_id": submission_id, "status": "SECURITY_BLOCKED", "error": str(ve)}

        # STAGE 2: SANDBOX_RUNNING (20%)
        submission.status = "SANDBOX_RUNNING"
        db.commit()
        notify_stage("SANDBOX_RUNNING", 20, attempt_id_str)

        sandbox_res = sandbox_engine.run_code(
            code=submission.source_code,
            mem_limit=settings.SANDBOX_MEM_LIMIT,
            cpu_quota=settings.SANDBOX_CPU_QUOTA,
            timeout_seconds=settings.SANDBOX_TIMEOUT_SECONDS
        )

        submission.execution_latency_ms = sandbox_res["execution_latency_ms"]
        submission.peak_memory_mb = sandbox_res["peak_memory_mb"]
        submission.exit_code = sandbox_res["exit_code"]
        submission.stdout = sandbox_res["stdout"]
        submission.stderr = sandbox_res["stderr"]

        if sandbox_res.get("timed_out"):
            submission.status = "TIMEOUT"
            submission.error_message = "Execution timed out limit."
            submission.completed_at = datetime.utcnow()
            db.commit()
            notify_stage("TIMEOUT", 100, attempt_id_str)
            return {"submission_id": submission_id, "status": "TIMEOUT"}

        # STAGE 3: TEST_CASE_EXECUTION (35%)
        submission.status = "TEST_CASE_EXECUTION"
        db.commit()
        notify_stage("TEST_CASE_EXECUTION", 35, attempt_id_str)

        test_cases = []
        if submission.question_id:
            test_cases = db.query(TestCase).filter(TestCase.question_id == submission.question_id).order_by(TestCase.test_case_order).all()

        functional_score, test_results = HiddenTestRunner.execute_test_cases(
            db=db,
            submission=submission,
            test_cases=test_cases,
            sandbox_engine=sandbox_engine
        )
        submission.functional_score = functional_score

        # STAGE 4: EXECUTION_COMPLETE (40%)
        submission.status = "EXECUTION_COMPLETE"
        db.commit()
        notify_stage("EXECUTION_COMPLETE", 40, attempt_id_str)

        # STAGE 5: MCP_CONTEXT (45%)
        submission.status = "MCP_CONTEXT"
        exam = db.query(Exam).filter(Exam.id == submission.exam_id).first()
        if not exam:
            exam = Exam(title="Python Assessment Task", description="Evaluation task", difficulty="intermediate")

        mcp_context, mcp_hash = MCPContextInjector.get_context(exam, submission.source_code)
        submission.mcp_context = mcp_context
        submission.mcp_context_hash = mcp_hash
        notify_stage("MCP_CONTEXT", 45, attempt_id_str)

        # STAGE 6: ANOMALY_ANALYSIS (55%)
        submission.status = "ANOMALY_ANALYSIS"
        telemetry = {
            "focus_lost_count": submission.focus_loss_count or 0,
            "paste_events_count": int((submission.paste_ratio or 0.0) * len(submission.source_code) / 100.0)
        }
        anomaly_res = BehavioralAnomalyOracle.analyze(telemetry, submission.source_code)
        submission.anomaly_score = anomaly_res["anomaly_score"]
        submission.paste_ratio = anomaly_res["paste_ratio"]
        submission.focus_loss_count = anomaly_res["focus_loss_count"]
        submission.typing_anomaly_score = anomaly_res["typing_anomaly_score"]
        notify_stage("ANOMALY_ANALYSIS", 55, attempt_id_str, {"anomaly_score": anomaly_res["anomaly_score"]})

        # STAGE 7 - 10: MULTI-AGENT A2A CONSENSUS (90%)
        submission.status = "A2A_CONSENSUS"
        notify_stage("A2A_CONSENSUS", 90, attempt_id_str)

        consensus_res = A2AConsensusEngine.run_consensus(
            db=db,
            submission=submission,
            submitted_code=submission.source_code,
            exam_title=exam.title,
            execution_metrics=sandbox_res,
            functional_score=functional_score
        )

        submission.mentor_score = consensus_res["mentor_score"]
        submission.qa_score = consensus_res["qa_score"]
        submission.consensus_score = consensus_res["consensus_score"]
        submission.consensus_confidence = consensus_res["confidence"]
        submission.a2a_consensus = {
            "mentor": consensus_res["mentor_res"],
            "qa": consensus_res["qa_res"],
            "security": consensus_res["sec_res"],
            "rounds": consensus_res["round_count"]
        }

        # STAGE 10: ADAPTIVE_ANALYSIS (95%)
        adaptive_res = AdaptiveChallengeEngine.evaluate_adaptive_recommendation(
            final_score=consensus_res["consensus_score"],
            functional_score=functional_score,
            latency_ms=sandbox_res["execution_latency_ms"]
        )
        submission.adaptive_challenge = adaptive_res["recommendation_text"]
        submission.final_score = consensus_res["consensus_score"]

        # Build Markdown Report
        report_md = f"""# Explain-Then-Grade Evaluation Report

## 1. Solution Understanding
Candidate submission evaluated against **"{exam.title}"**.

## 2. Functional Test Case Results
- **Functional Score**: `{functional_score}%`
- **Total Test Cases**: `{len(test_results)}`

## 3. Multi-Agent Evaluation Scores
- **Mentor Agent Score**: `{consensus_res['mentor_score']} / 100`
- **QA Auditor Score**: `{consensus_res['qa_score']} / 100`
- **Security Agent Score**: `{consensus_res.get('security_score', consensus_res.get('sec_score', 100.0))} / 100`
- **A2A Negotiation Rounds**: `{consensus_res['round_count']}`

## 4. Adaptive Challenge Recommendation
`{adaptive_res['recommendation_text']}`

---

## 5. Final Grade
### **FINAL GRADE: {consensus_res['consensus_score']} / 100**
"""
        submission.evaluation_report = report_md

        # STAGE 11: FINALIZED (100%)
        submission.status = "FINALIZED" if sandbox_res["exit_code"] == 0 else "FAILED"
        submission.completed_at = datetime.utcnow()

        if submission.attempt_id:
            attempt = db.query(ExamAttempt).filter(ExamAttempt.id == submission.attempt_id).first()
            if attempt:
                attempt.total_score = consensus_res["consensus_score"]
                attempt.status = "COMPLETED"
                attempt.completed_at = datetime.utcnow()

        db.commit()
        notify_stage("FINALIZED", 100, attempt_id_str, {"final_score": float(consensus_res["consensus_score"])})

        logger.info(f"Task {task_id}: Finalized submission {submission_id} with score {consensus_res['consensus_score']}")

        return {
            "submission_id": submission_id,
            "status": submission.status,
            "final_score": float(consensus_res["consensus_score"]),
            "functional_score": functional_score,
            "execution_latency_ms": sandbox_res["execution_latency_ms"]
        }

    except Exception as exc:
        logger.error(f"Task {task_id}: Error processing submission {submission_id}: {exc}", exc_info=True)
        db.rollback()
        try:
            sub = db.query(SubmissionFact).filter(SubmissionFact.submission_id == submission_id).first()
            if sub:
                sub.status = "FAILED"
                sub.error_message = f"Pipeline Task Error: {str(exc)}"
                sub.completed_at = datetime.utcnow()
                db.commit()
        except Exception:
            pass
        raise self.retry(exc=exc, countdown=5)
    finally:
        db.close()
