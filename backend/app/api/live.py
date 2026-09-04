import uuid
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.database.models import ExamAttempt, Exam, SubmissionFact, User
from app.api.auth import get_current_user

router = APIRouter(prefix="/live", tags=["Real-Time Recruiter Monitoring"])

@router.get("/exams")
def get_live_exams_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Real-time recruiter dashboard listing active exams and current attempt counts."""
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Recruiter or Admin authorization required.")

    active_exams = db.query(Exam).filter(Exam.is_active == True).all()
    results = []

    for exam in active_exams:
        active_attempts = db.query(func.count(ExamAttempt.id)).filter(
            ExamAttempt.exam_id == exam.id,
            ExamAttempt.status.in_(["STARTED", "IN_PROGRESS"])
        ).scalar() or 0

        total_submissions = db.query(func.count(SubmissionFact.submission_id)).filter(
            SubmissionFact.exam_id == exam.id
        ).scalar() or 0

        results.append({
            "exam_id": str(exam.id),
            "title": exam.title,
            "difficulty": exam.difficulty,
            "is_published": exam.is_published,
            "active_candidates_count": active_attempts,
            "total_submissions_count": total_submissions
        })

    return {"live_exams": results}

@router.get("/exams/{exam_id}")
def get_live_exam_detail(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Detailed live monitoring view for a specific exam showing active candidate attempts."""
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Recruiter or Admin authorization required.")

    try:
        e_uuid = uuid.UUID(exam_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid exam_id UUID format.")

    exam = db.query(Exam).filter(Exam.id == e_uuid).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    attempts = db.query(ExamAttempt).filter(ExamAttempt.exam_id == exam.id).all()
    attempt_list = []

    for att in attempts:
        attempt_list.append({
            "attempt_id": str(att.id),
            "candidate_id": str(att.candidate_id),
            "status": att.status,
            "started_at": att.started_at,
            "expires_at": att.expires_at,
            "total_score": float(att.total_score or 0.0)
        })

    return {
        "exam_id": str(exam.id),
        "title": exam.title,
        "total_attempts": len(attempts),
        "attempts": attempt_list
    }

@router.get("/attempts/{attempt_id}")
def get_live_attempt_monitoring(
    attempt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Detailed monitoring view for an individual candidate attempt."""
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Recruiter or Admin authorization required.")

    try:
        a_uuid = uuid.UUID(attempt_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attempt_id UUID format.")

    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == a_uuid).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found.")

    submissions = db.query(SubmissionFact).filter(SubmissionFact.attempt_id == attempt.id).all()
    latest_sub = submissions[-1] if submissions else None

    return {
        "attempt_id": str(attempt.id),
        "candidate_id": str(attempt.candidate_id),
        "status": attempt.status,
        "started_at": attempt.started_at,
        "expires_at": attempt.expires_at,
        "submissions_count": len(submissions),
        "latest_submission_status": latest_sub.status if latest_sub else None,
        "latest_anomaly_score": latest_sub.anomaly_score if latest_sub else 0.0,
        "latest_final_score": float(latest_sub.final_score) if (latest_sub and latest_sub.final_score is not None) else None
    }
