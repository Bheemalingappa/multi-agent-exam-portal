import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import ExamAttempt, Exam, User
from app.api.auth import get_current_user
from app.api.student_access import require_candidate_exam_access
from app.schemas.attempt import AttemptResponseSchema

router = APIRouter(tags=["Exam Attempt Management"])

@router.post("/exams/{exam_id}/attempts", response_model=AttemptResponseSchema, status_code=status.HTTP_201_CREATED)
def start_exam_attempt(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Candidate starts a new exam attempt.
    Calculates server-side started_at and expires_at based on exam duration.
    Verifies candidate has an active assignment and hasn't exceeded max_attempts.
    """
    try:
        e_uuid = uuid.UUID(exam_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid exam_id UUID format.")

    exam = db.query(Exam).filter(Exam.id == e_uuid).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    if current_user.role == "candidate":
        require_candidate_exam_access(db, exam, current_user)

    # Check candidate attempt count against max_attempts
    existing_count = db.query(ExamAttempt).filter(
        ExamAttempt.candidate_id == current_user.id,
        ExamAttempt.exam_id == exam.id
    ).count()

    if existing_count >= exam.max_attempts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Attempt limit reached. Maximum allowed attempts for this exam: {exam.max_attempts}."
        )

    now = datetime.utcnow()
    expires = now + timedelta(minutes=exam.duration_minutes)

    new_attempt = ExamAttempt(
        candidate_id=current_user.id,
        exam_id=exam.id,
        status="STARTED",
        started_at=now,
        expires_at=expires,
        total_score=0.00,
        max_score=exam.max_score
    )

    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)

    remaining = max(int((expires - now).total_seconds()), 0)

    return AttemptResponseSchema(
        id=str(new_attempt.id),
        candidate_id=str(new_attempt.candidate_id),
        exam_id=str(new_attempt.exam_id),
        status=new_attempt.status,
        started_at=new_attempt.started_at,
        expires_at=new_attempt.expires_at,
        remaining_seconds=remaining,
        submitted_at=new_attempt.submitted_at,
        completed_at=new_attempt.completed_at,
        total_score=float(new_attempt.total_score or 0.0),
        max_score=float(new_attempt.max_score or 100.0)
    )

@router.get("/attempts/{attempt_id}", response_model=AttemptResponseSchema)
def get_attempt_by_id(
    attempt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves exam attempt state and remaining time.
    Calculates server-side timer. Automatically transitions to EXPIRED if current time >= expires_at.
    """
    try:
        a_uuid = uuid.UUID(attempt_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attempt_id UUID format.")

    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == a_uuid).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found.")

    # IDOR Protection: Candidate can only read their own attempt
    if current_user.role == "candidate" and attempt.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only access your own exam attempts.")

    if current_user.role == "candidate":
        exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found for attempt.")
        require_candidate_exam_access(db, exam, current_user)

    # Server-Side Timer Calculation
    now = datetime.utcnow()
    if now >= attempt.expires_at and attempt.status in ["STARTED", "IN_PROGRESS"]:
        attempt.status = "EXPIRED"
        db.commit()

    remaining = max(int((attempt.expires_at - now).total_seconds()), 0)

    return AttemptResponseSchema(
        id=str(attempt.id),
        candidate_id=str(attempt.candidate_id),
        exam_id=str(attempt.exam_id),
        status=attempt.status,
        started_at=attempt.started_at,
        expires_at=attempt.expires_at,
        remaining_seconds=remaining,
        submitted_at=attempt.submitted_at,
        completed_at=attempt.completed_at,
        total_score=float(attempt.total_score or 0.0),
        max_score=float(attempt.max_score or 100.0)
    )

@router.post("/attempts/{attempt_id}/submit", response_model=AttemptResponseSchema)
def submit_exam_attempt(
    attempt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submits the exam attempt and triggers status transition to SUBMITTED."""
    try:
        a_uuid = uuid.UUID(attempt_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attempt_id UUID format.")

    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == a_uuid).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found.")

    if attempt.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only submit your own exam attempt.")

    if current_user.role == "candidate":
        exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found for attempt.")
        require_candidate_exam_access(db, exam, current_user)

    now = datetime.utcnow()
    if now >= attempt.expires_at:
        attempt.status = "EXPIRED"
        db.commit()
        raise HTTPException(status_code=400, detail="Cannot submit: Exam attempt has expired.")

    if attempt.status in ["SUBMITTED", "COMPLETED", "EXPIRED", "CANCELLED"]:
        raise HTTPException(status_code=400, detail=f"Cannot submit attempt with status '{attempt.status}'.")

    attempt.status = "SUBMITTED"
    attempt.submitted_at = now
    db.commit()
    db.refresh(attempt)

    remaining = max(int((attempt.expires_at - now).total_seconds()), 0)

    return AttemptResponseSchema(
        id=str(attempt.id),
        candidate_id=str(attempt.candidate_id),
        exam_id=str(attempt.exam_id),
        status=attempt.status,
        started_at=attempt.started_at,
        expires_at=attempt.expires_at,
        remaining_seconds=remaining,
        submitted_at=attempt.submitted_at,
        completed_at=attempt.completed_at,
        total_score=float(attempt.total_score or 0.0),
        max_score=float(attempt.max_score or 100.0)
    )

@router.post("/attempts/{attempt_id}/cancel", response_model=AttemptResponseSchema)
def cancel_exam_attempt(
    attempt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancels an active exam attempt."""
    try:
        a_uuid = uuid.UUID(attempt_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attempt_id UUID format.")

    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == a_uuid).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found.")

    if current_user.role == "candidate" and attempt.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only cancel your own exam attempt.")

    if current_user.role == "candidate":
        exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found for attempt.")
        require_candidate_exam_access(db, exam, current_user)

    attempt.status = "CANCELLED"
    db.commit()
    db.refresh(attempt)

    now = datetime.utcnow()
    remaining = max(int((attempt.expires_at - now).total_seconds()), 0)

    return AttemptResponseSchema(
        id=str(attempt.id),
        candidate_id=str(attempt.candidate_id),
        exam_id=str(attempt.exam_id),
        status=attempt.status,
        started_at=attempt.started_at,
        expires_at=attempt.expires_at,
        remaining_seconds=remaining,
        submitted_at=attempt.submitted_at,
        completed_at=attempt.completed_at,
        total_score=float(attempt.total_score or 0.0),
        max_score=float(attempt.max_score or 100.0)
    )
