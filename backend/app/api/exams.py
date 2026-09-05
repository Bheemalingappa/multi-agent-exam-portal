import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from pydantic import BaseModel, Field
from app.database.session import get_db
from app.database.models import Exam, User, ExamAssignment, QuestionPaper
from app.api.auth import get_current_user
from app.api.student_access import get_student_class_level, require_candidate_exam_access
from app.schemas.exam import ExamCreateSchema, ExamUpdateSchema, ExamResponseSchema

router = APIRouter(prefix="/exams", tags=["Exam Management"])

from datetime import datetime

class AssignExamRequest(BaseModel):
    class_level: int = Field(..., ge=1, le=12)
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    is_active: Optional[bool] = True

@router.post("", response_model=ExamResponseSchema, status_code=status.HTTP_201_CREATED)
def create_exam(
    payload: ExamCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a new Exam catalog entry. Requires Recruiter or Admin role authorization."""
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Recruiter or Admin access required.")

    new_exam = Exam(
        title=payload.title,
        description=payload.description,
        class_level=payload.class_level,
        subject=payload.subject,
        language=payload.language,
        difficulty=payload.difficulty,
        duration_minutes=payload.duration_minutes,
        max_score=payload.max_score,
        max_attempts=payload.max_attempts,
        is_active=True,
        is_published=False,
        created_by=current_user.id
    )

    db.add(new_exam)
    db.commit()
    db.refresh(new_exam)

    return ExamResponseSchema(
        id=str(new_exam.id),
        title=new_exam.title,
        description=new_exam.description,
        class_level=new_exam.class_level,
        subject=new_exam.subject,
        language=new_exam.language,
        difficulty=new_exam.difficulty,
        duration_minutes=new_exam.duration_minutes,
        max_score=float(new_exam.max_score),
        max_attempts=new_exam.max_attempts,
        is_active=new_exam.is_active,
        is_published=new_exam.is_published,
        created_at=new_exam.created_at
    )

@router.get("", response_model=List[ExamResponseSchema])
def list_exams(
    class_level: Optional[int] = Query(None, ge=1, le=12, description="Filter exams by Class level (1 to 12)"),
    subject: Optional[str] = Query(None, description="Filter exams by subject name"),
    language: Optional[str] = Query(None, description="Filter exams by language"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists available exams. Candidates only see published exams explicitly assigned to their class."""
    query = db.query(Exam)

    if current_user.role == "candidate":
        target_class = get_student_class_level(current_user)

        assignments = db.query(ExamAssignment).filter(
            ExamAssignment.class_level == target_class,
            ExamAssignment.status == "ACTIVE"
        ).all()

        assigned_exam_ids = [
            assignment.exam_id
            for assignment in assignments
            if assignment.exam_id is not None
        ]

        if not assigned_exam_ids:
            return []

        query = query.filter(
            Exam.is_active == True,
            Exam.is_published == True,
            Exam.id.in_(assigned_exam_ids)
        )

    if current_user.role != "candidate" and class_level is not None:
        query = query.filter(Exam.class_level == class_level)

    if subject is not None and subject.strip() != "":
        query = query.filter(Exam.subject.ilike(f"%{subject.strip()}%"))

    if language is not None and language.strip() != "":
        query = query.filter(Exam.language.ilike(f"%{language.strip()}%"))

    exams = query.order_by(Exam.created_at.desc()).all()

    return [
        ExamResponseSchema(
            id=str(e.id),
            title=e.title,
            description=e.description,
            class_level=e.class_level,
            subject=e.subject,
            language=e.language,
            difficulty=e.difficulty,
            duration_minutes=e.duration_minutes,
            max_score=float(e.max_score),
            max_attempts=e.max_attempts,
            is_active=e.is_active,
            is_published=e.is_published,
            created_at=e.created_at
        )
        for e in exams
    ]

@router.get("/{exam_id}", response_model=ExamResponseSchema)
def get_exam_by_id(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves single exam by ID. Candidates must have an active assignment to access."""
    try:
        e_uuid = uuid.UUID(exam_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid exam_id UUID format.")

    exam = db.query(Exam).filter(Exam.id == e_uuid).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    if current_user.role == "candidate":
        require_candidate_exam_access(db, exam, current_user)

    return ExamResponseSchema(
        id=str(exam.id),
        title=exam.title,
        description=exam.description,
        class_level=exam.class_level,
        subject=exam.subject,
        language=exam.language,
        difficulty=exam.difficulty,
        duration_minutes=exam.duration_minutes,
        max_score=float(exam.max_score),
        max_attempts=exam.max_attempts,
        is_active=exam.is_active,
        is_published=exam.is_published,
        created_at=exam.created_at
    )

    return ExamResponseSchema(
        id=str(exam.id),
        title=exam.title,
        description=exam.description,
        class_level=exam.class_level,
        subject=exam.subject,
        language=exam.language,
        difficulty=exam.difficulty,
        duration_minutes=exam.duration_minutes,
        max_score=float(exam.max_score),
        max_attempts=exam.max_attempts,
        is_active=exam.is_active,
        is_published=exam.is_published,
        created_at=exam.created_at
    )

@router.patch("/{exam_id}", response_model=ExamResponseSchema)
def update_exam(
    exam_id: str,
    payload: ExamUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Updates an existing exam. Requires Recruiter or Admin role."""
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Recruiter or Admin access required.")

    try:
        e_uuid = uuid.UUID(exam_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid exam_id UUID format.")

    exam = db.query(Exam).filter(Exam.id == e_uuid).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    if payload.title is not None:
        exam.title = payload.title
    if payload.description is not None:
        exam.description = payload.description
    if payload.class_level is not None:
        exam.class_level = payload.class_level
    if payload.subject is not None:
        exam.subject = payload.subject
    if payload.language is not None:
        exam.language = payload.language
    if payload.difficulty is not None:
        exam.difficulty = payload.difficulty
    if payload.duration_minutes is not None:
        exam.duration_minutes = payload.duration_minutes
    if payload.max_score is not None:
        exam.max_score = payload.max_score
    if payload.max_attempts is not None:
        exam.max_attempts = payload.max_attempts
    if payload.is_active is not None:
        exam.is_active = payload.is_active

    db.commit()
    db.refresh(exam)

    return ExamResponseSchema(
        id=str(exam.id),
        title=exam.title,
        description=exam.description,
        class_level=exam.class_level,
        subject=exam.subject,
        language=exam.language,
        difficulty=exam.difficulty,
        duration_minutes=exam.duration_minutes,
        max_score=float(exam.max_score),
        max_attempts=exam.max_attempts,
        is_active=exam.is_active,
        is_published=exam.is_published,
        created_at=exam.created_at
    )

@router.post("/{exam_id}/assign")
def assign_exam_endpoint(
    exam_id: str,
    payload: AssignExamRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assigns a published exam to a specific class level. Requires Recruiter or Admin role."""
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Recruiter or Admin access required.")

    try:
        e_uuid = uuid.UUID(exam_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid exam_id UUID format.")

    exam = db.query(Exam).filter(Exam.id == e_uuid).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    if current_user.role != "admin" and exam.created_by is not None and exam.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this exam.")

    if not exam.is_published:
        raise HTTPException(status_code=400, detail="Exam must be published before it can be assigned to a class.")

    if payload.class_level != exam.class_level:
        raise HTTPException(
            status_code=400,
            detail=f"Target class_level ({payload.class_level}) does not match exam class_level ({exam.class_level})."
        )

    assignment = db.query(ExamAssignment).filter(
        ExamAssignment.exam_id == exam.id,
        ExamAssignment.class_level == payload.class_level
    ).first()

    is_act = payload.is_active if payload.is_active is not None else True
    status_val = "ACTIVE" if is_act else "INACTIVE"

    if not assignment:
        assignment = ExamAssignment(
            exam_id=exam.id,
            class_level=payload.class_level,
            assigned_by=current_user.id,
            status=status_val,
            start_at=payload.start_at,
            end_at=payload.end_at,
            is_active=is_act
        )
        db.add(assignment)
    else:
        assignment.status = status_val
        assignment.is_active = is_act
        assignment.assigned_by = current_user.id
        if payload.start_at is not None:
            assignment.start_at = payload.start_at
        if payload.end_at is not None:
            assignment.end_at = payload.end_at

    # Update QuestionPaper status if exists
    qp = db.query(QuestionPaper).filter(QuestionPaper.published_exam_id == exam.id).first()
    if qp:
        qp.status = "ASSIGNED"

    db.commit()
    db.refresh(assignment)

    return {
        "id": str(assignment.id),
        "exam_id": str(assignment.exam_id),
        "class_level": assignment.class_level,
        "start_at": assignment.start_at.isoformat() if assignment.start_at else None,
        "end_at": assignment.end_at.isoformat() if assignment.end_at else None,
        "is_active": assignment.is_active,
        "assigned_by": str(assignment.assigned_by) if assignment.assigned_by else None,
        "status": assignment.status,
        "created_at": assignment.created_at
    }

@router.post("/{exam_id}/publish", response_model=ExamResponseSchema)
def publish_exam(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Publishes an exam making it visible to candidates."""
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Recruiter or Admin access required.")

    try:
        e_uuid = uuid.UUID(exam_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid exam_id UUID format.")

    exam = db.query(Exam).filter(Exam.id == e_uuid).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    exam.is_published = True
    db.commit()
    db.refresh(exam)

    return ExamResponseSchema(
        id=str(exam.id),
        title=exam.title,
        description=exam.description,
        class_level=exam.class_level,
        subject=exam.subject,
        language=exam.language,
        difficulty=exam.difficulty,
        duration_minutes=exam.duration_minutes,
        max_score=float(exam.max_score),
        max_attempts=exam.max_attempts,
        is_active=exam.is_active,
        is_published=exam.is_published,
        created_at=exam.created_at
    )

@router.post("/{exam_id}/unpublish", response_model=ExamResponseSchema)
def unpublish_exam(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Unpublishes an exam hiding it from candidate catalogs."""
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Recruiter or Admin access required.")

    try:
        e_uuid = uuid.UUID(exam_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid exam_id UUID format.")

    exam = db.query(Exam).filter(Exam.id == e_uuid).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    exam.is_published = False
    db.commit()
    db.refresh(exam)

    return ExamResponseSchema(
        id=str(exam.id),
        title=exam.title,
        description=exam.description,
        class_level=exam.class_level,
        subject=exam.subject,
        language=exam.language,
        difficulty=exam.difficulty,
        duration_minutes=exam.duration_minutes,
        max_score=float(exam.max_score),
        max_attempts=exam.max_attempts,
        is_active=exam.is_active,
        is_published=exam.is_published,
        created_at=exam.created_at
    )
