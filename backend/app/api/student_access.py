from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.models import Exam, ExamAssignment, User


def get_student_class_level(user: User) -> int:
    if user.class_level is None:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Student class level is not configured."
        )
    return user.class_level


def make_naive(dt):
    if dt is not None and hasattr(dt, "tzinfo") and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def has_active_assignment_for_student(db: Session, exam: Exam, student: User) -> bool:
    student_class = get_student_class_level(student)
    now = datetime.utcnow()
    assignments = db.query(ExamAssignment).filter(
        ExamAssignment.exam_id == exam.id,
        ExamAssignment.class_level == student_class,
        ExamAssignment.status == "ACTIVE",
        ExamAssignment.is_active == True
    ).all()

    for assignment in assignments:
        st = make_naive(assignment.start_at)
        et = make_naive(assignment.end_at)
        if st and now < st:
            continue
        if et and now > et:
            continue
        return True

    return False


def require_candidate_exam_access(db: Session, exam: Exam, student: User) -> None:
    if not exam.is_published or not exam.is_active:
        raise HTTPException(status_code=403, detail="Forbidden: Exam is not published or active.")
    if not has_active_assignment_for_student(db, exam, student):
        raise HTTPException(status_code=403, detail="Forbidden: Exam is not assigned to your class.")
