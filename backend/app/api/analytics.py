from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import User
from app.api.auth import get_current_user
from app.analytics.service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Advanced Analytics & Intelligence"])

@router.get("/student/summary")
def get_student_analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Student Results Dashboard: Overview metrics, latest result, and recent results list.
    Only accessible by candidates for their own data.
    """
    if current_user.role not in ["candidate", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Only candidates can access candidate summary analytics."
        )
    return AnalyticsService.get_student_summary(db, str(current_user.id))

@router.get("/student/performance")
def get_student_performance_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Student Performance Analytics: Score trend timeline, subject breakdown, and grade distribution.
    Only accessible by candidates for their own data.
    """
    if current_user.role not in ["candidate", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Only candidates can access candidate performance analytics."
        )
    return AnalyticsService.get_student_performance(db, str(current_user.id))

@router.get("/teacher/summary")
def get_teacher_analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Teacher Portal Summary: Overview metrics across all exams owned/managed by teacher.
    Only accessible by recruiter/teacher roles.
    """
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Recruiter/Teacher authorization required."
        )
    return AnalyticsService.get_teacher_summary(db, str(current_user.id))

@router.get("/exams/{exam_id}/performance")
def get_exam_performance_analytics(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Exam-Level Performance View: Submissions %, avg/highest/lowest score, pass rate,
    grade distribution, and exact_topic performance for owned exam.
    """
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Recruiter/Teacher authorization required."
        )
    try:
        return AnalyticsService.get_exam_performance(db, exam_id, str(current_user.id))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

@router.get("/exams/{exam_id}/questions")
def get_exam_questions_analytics(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Question-Wise Analytics: Itemized attempts, correct/incorrect/skipped counts,
    accuracy %, average marks, and difficulty identification for owned exam.
    """
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Recruiter/Teacher authorization required."
        )
    try:
        return AnalyticsService.get_exam_questions_analytics(db, exam_id, str(current_user.id))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

@router.get("/exams/{exam_id}/students")
def get_exam_students_roster_analytics(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Student Performance Roster Table: Itemized candidate scores, %, grades, submission dates,
    evaluation statuses, and performance flags for owned exam.
    """
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Recruiter/Teacher authorization required."
        )
    try:
        return AnalyticsService.get_exam_students_roster(db, exam_id, str(current_user.id))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
