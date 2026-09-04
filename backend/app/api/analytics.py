from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import User
from app.api.auth import get_current_user
from app.analytics.service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Advanced Analytics & Intelligence"])

@router.get("/overview")
def get_analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Recruiter authorization required.")
    return AnalyticsService.get_overview_metrics(db)

@router.get("/questions")
def get_question_intelligence(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden.")
    return AnalyticsService.get_question_intelligence(db)
