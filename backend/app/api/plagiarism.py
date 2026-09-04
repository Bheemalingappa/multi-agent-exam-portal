import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import SubmissionFact, PlagiarismResultFact, User
from app.api.auth import get_current_user
from app.plagiarism.detector import PlagiarismDetector

router = APIRouter(prefix="/plagiarism", tags=["Plagiarism Detection Engine"])

class PlagiarismCheckSchema(BaseModel):
    submission_id: str
    compare_with_submission_id: str

@router.post("/check")
def check_plagiarism_similarity(
    payload: PlagiarismCheckSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Recruiter authorization required.")

    try:
        s1 = db.query(SubmissionFact).filter(SubmissionFact.submission_id == uuid.UUID(payload.submission_id)).first()
        s2 = db.query(SubmissionFact).filter(SubmissionFact.submission_id == uuid.UUID(payload.compare_with_submission_id)).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid submission UUID format.")

    if not s1 or not s2:
        raise HTTPException(status_code=404, detail="Submissions for comparison not found.")

    res = PlagiarismDetector.evaluate_similarity(s1.source_code, s2.source_code)

    record = PlagiarismResultFact(
        submission_id=s1.submission_id,
        compared_submission_id=s2.submission_id,
        ast_similarity_score=res["ast_similarity_score"],
        token_similarity_score=res["token_similarity_score"],
        plagiarism_risk_level=res["plagiarism_risk_level"],
        matching_evidence=res["matching_evidence"]
    )
    db.add(record)
    db.commit()

    return res
