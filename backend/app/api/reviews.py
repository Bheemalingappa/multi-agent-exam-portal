import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import SubmissionFact, HumanReviewFact, User
from app.api.auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["Human-in-the-Loop Recruiter Reviews"])

class HumanReviewCreateSchema(BaseModel):
    override_score: float = Field(ge=0.0, le=100.0)
    review_status: str = "APPROVED"
    reason: str

@router.post("/{submission_id}")
def record_recruiter_review(
    submission_id: str,
    payload: HumanReviewCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Human-in-the-Loop AI Review endpoint allowing authorized recruiters to override
    agent consensus scores with an explicit reason recorded in fact_human_reviews.
    """
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Recruiter or Admin authorization required.")

    try:
        s_uuid = uuid.UUID(submission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid submission_id UUID format.")

    submission = db.query(SubmissionFact).filter(SubmissionFact.submission_id == s_uuid).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission fact record not found.")

    original_score = float(submission.final_score or 0.0)

    # Record human review override
    review_record = HumanReviewFact(
        submission_id=submission.submission_id,
        reviewer_id=current_user.id,
        original_score=original_score,
        override_score=payload.override_score,
        review_status=payload.review_status,
        reason=payload.reason
    )
    db.add(review_record)

    # Update authoritative final score on submission
    submission.final_score = payload.override_score
    submission.evaluation_report = (submission.evaluation_report or "") + f"\n\n### 📝 Human Recruiter Override\n- **Original Score**: `{original_score}`\n- **Override Score**: `{payload.override_score}`\n- **Reviewer**: `{current_user.email}`\n- **Reason**: {payload.reason}"
    db.commit()

    return {
        "status": "reviewed",
        "submission_id": submission_id,
        "original_score": original_score,
        "override_score": payload.override_score,
        "reason": payload.reason
    }
