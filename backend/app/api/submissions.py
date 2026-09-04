import uuid
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.database.models import SubmissionFact, Exam, Question, ExamAttempt, SandboxProfile, User
from app.api.auth import get_current_user
from app.api.student_access import require_candidate_exam_access
from app.pipeline.tasks import evaluate_submission_task

router = APIRouter(prefix="/submissions", tags=["Submissions"])

MAX_SOURCE_CODE_BYTES = 100000  # 100 KB limit

class TelemetryPayloadSchema(BaseModel):
    typing_events: List[Any] = Field(default_factory=list, max_length=1000)
    focus_events: List[Any] = Field(default_factory=list, max_length=1000)
    paste_events: List[Any] = Field(default_factory=list, max_length=1000)
    typing_speed_wpm: float = 45.0
    focus_lost_count: int = 0
    paste_events_count: int = 0

class SubmissionCreateSchema(BaseModel):
    exam_id: Optional[str] = None
    attempt_id: Optional[str] = None
    question_id: Optional[str] = None
    language: str = "python"
    code: str
    telemetry: Optional[TelemetryPayloadSchema] = None

class SubmissionResponseSchema(BaseModel):
    submission_id: str
    celery_task_id: Optional[str]
    status: str
    message: str

class SubmissionDetailSchema(BaseModel):
    submission_id: str
    candidate_id: str
    exam_id: str
    attempt_id: Optional[str]
    question_id: Optional[str]
    sandbox_profile_id: str
    language: str
    source_code: str
    status: str
    celery_task_id: Optional[str]
    static_analysis_status: Optional[str]
    security_risk_level: Optional[str]
    functional_score: Optional[float]
    execution_latency_ms: Optional[float]
    peak_memory_mb: Optional[float]
    exit_code: Optional[int]
    stdout: Optional[str]
    stderr: Optional[str]
    anomaly_score: Optional[float]
    paste_ratio: Optional[float]
    focus_loss_count: Optional[int]
    typing_anomaly_score: Optional[float]
    mcp_context: Optional[Dict[str, Any]]
    mcp_context_hash: Optional[str]
    mentor_score: Optional[float]
    qa_score: Optional[float]
    consensus_score: Optional[float]
    consensus_confidence: Optional[float]
    a2a_consensus: Optional[Dict[str, Any]]
    adaptive_challenge: Optional[str]
    evaluation_report: Optional[str]
    final_score: Optional[float]
    error_message: Optional[str]
    started_at: Optional[Any]
    completed_at: Optional[Any]
    created_at: Any

@router.post("", response_model=SubmissionResponseSchema, status_code=status.HTTP_202_ACCEPTED)
def submit_code_for_evaluation(
    payload: SubmissionCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ingests candidate code payload, verifies size limits, links attempt & question,
    creates QUEUED submission record in PostgreSQL, and dispatches Celery task.
    """
    if not payload.code.strip():
        raise HTTPException(status_code=400, detail="Source code payload cannot be empty.")

    # 1. Source Code Size Limit Check (100 KB max)
    code_bytes = len(payload.code.encode("utf-8"))
    if code_bytes > MAX_SOURCE_CODE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Payload Too Large: Source code size ({code_bytes} bytes) exceeds maximum limit of {MAX_SOURCE_CODE_BYTES} bytes."
        )

    # 2. Resolve & Validate Exam
    exam = None
    if payload.exam_id:
        try:
            exam_uuid = uuid.UUID(payload.exam_id)
            exam = db.query(Exam).filter(Exam.id == exam_uuid).first()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid exam_id UUID format.")

    if not exam:
        exam = db.query(Exam).filter(Exam.is_active == True).first()
        if not exam:
            exam = Exam(
                title="Python Assessment Task",
                description="Evaluation task",
                difficulty="intermediate",
                duration_minutes=60,
                max_score=100.00,
                is_active=True
            )
            db.add(exam)
            db.commit()
            db.refresh(exam)

    if current_user.role == "candidate":
        require_candidate_exam_access(db, exam, current_user)

    # 3. Validate Attempt Ownership & Active Timer (if attempt_id specified)
    attempt_uuid = None
    if payload.attempt_id:
        try:
            attempt_uuid = uuid.UUID(payload.attempt_id)
            attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_uuid).first()
            if not attempt:
                raise HTTPException(status_code=404, detail="Exam attempt not found.")

            if attempt.candidate_id != current_user.id:
                raise HTTPException(status_code=403, detail="Forbidden: Attempt belongs to another candidate.")
            if attempt.exam_id != exam.id:
                raise HTTPException(status_code=400, detail="Attempt does not belong to the submitted exam.")

            if attempt.status in ["EXPIRED", "CANCELLED", "COMPLETED"]:
                raise HTTPException(status_code=400, detail=f"Cannot submit: Exam attempt is in status '{attempt.status}'.")

        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid attempt_id UUID format.")

    # 4. Validate Question (if question_id specified)
    question_uuid = None
    if payload.question_id:
        try:
            question_uuid = uuid.UUID(payload.question_id)
            q = db.query(Question).filter(Question.id == question_uuid).first()
            if not q:
                raise HTTPException(status_code=404, detail="Question not found.")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid question_id UUID format.")

    # 5. Resolve Sandbox Profile
    profile = db.query(SandboxProfile).first()
    if not profile:
        profile = SandboxProfile(
            name="default_python_sandbox",
            memory_limit_mb=128,
            cpu_limit=0.50,
            timeout_seconds=2
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    telemetry_dict = payload.telemetry.dict() if payload.telemetry else {}
    focus_losses = telemetry_dict.get("focus_lost_count", len(telemetry_dict.get("focus_events", [])))
    pastes = telemetry_dict.get("paste_events_count", len(telemetry_dict.get("paste_events", [])))

    new_submission = SubmissionFact(
        candidate_id=current_user.id,
        exam_id=exam.id,
        attempt_id=attempt_uuid,
        question_id=question_uuid,
        sandbox_profile_id=profile.id,
        language=payload.language or "python",
        source_code=payload.code,
        status="QUEUED",
        focus_loss_count=focus_losses,
        paste_ratio=round((pastes * 100.0) / max(len(payload.code), 1), 2)
    )

    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    sub_id_str = str(new_submission.submission_id)
    task_id = None

    try:
        task_res = evaluate_submission_task.delay(sub_id_str)
        task_id = task_res.id
        new_submission.celery_task_id = task_id
        db.commit()
    except Exception as celery_err:
        new_submission.celery_task_id = f"sync_fallback_{sub_id_str[:8]}"
        db.commit()
        evaluate_submission_task(sub_id_str)

    return SubmissionResponseSchema(
        submission_id=sub_id_str,
        celery_task_id=task_id,
        status="QUEUED",
        message="Code submission queued successfully for asynchronous evaluation pipeline."
    )

@router.get("/{submission_id}", response_model=SubmissionDetailSchema)
def get_submission_by_id(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves full submission details.
    IDOR Protection: Candidates can only access their own submissions.
    """
    try:
        sub_uuid = uuid.UUID(submission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid submission UUID format.")

    submission = db.query(SubmissionFact).filter(SubmissionFact.submission_id == sub_uuid).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission record not found.")

    if current_user.role == "candidate" and submission.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only view your own submission records.")

    return SubmissionDetailSchema(
        submission_id=str(submission.submission_id),
        candidate_id=str(submission.candidate_id),
        exam_id=str(submission.exam_id),
        attempt_id=str(submission.attempt_id) if submission.attempt_id else None,
        question_id=str(submission.question_id) if submission.question_id else None,
        sandbox_profile_id=str(submission.sandbox_profile_id),
        language=submission.language,
        source_code=submission.source_code,
        status=submission.status,
        celery_task_id=submission.celery_task_id,
        static_analysis_status=submission.static_analysis_status,
        security_risk_level=submission.security_risk_level,
        functional_score=float(submission.functional_score) if submission.functional_score is not None else None,
        execution_latency_ms=submission.execution_latency_ms,
        peak_memory_mb=submission.peak_memory_mb,
        exit_code=submission.exit_code,
        stdout=submission.stdout,
        stderr=submission.stderr,
        anomaly_score=submission.anomaly_score,
        paste_ratio=submission.paste_ratio,
        focus_loss_count=submission.focus_loss_count,
        typing_anomaly_score=submission.typing_anomaly_score,
        mcp_context=submission.mcp_context,
        mcp_context_hash=submission.mcp_context_hash,
        mentor_score=float(submission.mentor_score) if submission.mentor_score is not None else None,
        qa_score=float(submission.qa_score) if submission.qa_score is not None else None,
        consensus_score=float(submission.consensus_score) if submission.consensus_score is not None else None,
        consensus_confidence=submission.consensus_confidence,
        a2a_consensus=submission.a2a_consensus,
        adaptive_challenge=submission.adaptive_challenge,
        evaluation_report=submission.evaluation_report,
        final_score=float(submission.final_score) if submission.final_score is not None else None,
        error_message=submission.error_message,
        started_at=submission.started_at,
        completed_at=submission.completed_at,
        created_at=submission.created_at
    )

@router.get("/analytics/dashboard")
def get_submission_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Computes aggregate analytics from PostgreSQL database. Requires Recruiter or Admin role."""
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Recruiter or Admin authorization required.")

    total_submissions = db.query(func.count(SubmissionFact.submission_id)).scalar() or 0
    completed_submissions = db.query(func.count(SubmissionFact.submission_id)).filter(
        SubmissionFact.status.in_(["FINALIZED", "COMPLETED", "EVALUATED"])
    ).scalar() or 0

    avg_score = db.query(func.avg(SubmissionFact.final_score)).scalar() or 0.0
    avg_func_score = db.query(func.avg(SubmissionFact.functional_score)).scalar() or 0.0
    avg_latency = db.query(func.avg(SubmissionFact.execution_latency_ms)).scalar() or 0.0

    return {
        "analytics": {
            "total_submissions": total_submissions,
            "completed_submissions": completed_submissions,
            "average_final_score": round(float(avg_score), 2),
            "average_functional_score": round(float(avg_func_score), 2),
            "average_execution_latency_ms": round(float(avg_latency), 2)
        }
    }
