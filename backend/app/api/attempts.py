import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.database.session import get_db
from app.database.models import ExamAttempt, Exam, User, QuestionPaper, Question, ExamEvaluation
from app.api.auth import get_current_user
from app.api.student_access import require_candidate_exam_access
from app.schemas.attempt import AttemptResponseSchema, AnswerSaveSchema
from app.schemas.evaluation import ExamEvaluationResponseSchema, StudentEvaluationSummarySchema, EvaluationRetryRequestSchema
from app.services.evaluation_service import evaluate_attempt_service

router = APIRouter(tags=["Exam Attempt Management"])

def make_naive(dt):
    if dt is not None and hasattr(dt, "tzinfo") and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

@router.post("/exams/{exam_id}/attempts", response_model=AttemptResponseSchema, status_code=status.HTTP_201_CREATED)
def start_exam_attempt(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Candidate starts a new exam attempt or resumes an existing active attempt.
    Calculates server-side started_at and expires_at based on exam duration.
    Enforces student class assignment & active datetime window via require_candidate_exam_access.
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

    now = datetime.utcnow()

    # Check for existing active attempt (Resume Attempt logic)
    existing_active = db.query(ExamAttempt).filter(
        ExamAttempt.candidate_id == current_user.id,
        ExamAttempt.exam_id == exam.id,
        ExamAttempt.status.in_(["STARTED", "IN_PROGRESS"])
    ).first()

    if existing_active:
        exp = make_naive(existing_active.expires_at)
        if now >= exp:
            existing_active.status = "EXPIRED"
            db.commit()
        else:
            remaining = max(int((exp - now).total_seconds()), 0)
            return AttemptResponseSchema(
                id=str(existing_active.id),
                candidate_id=str(existing_active.candidate_id),
                exam_id=str(existing_active.exam_id),
                status=existing_active.status,
                started_at=existing_active.started_at,
                expires_at=existing_active.expires_at,
                remaining_seconds=remaining,
                submitted_at=existing_active.submitted_at,
                completed_at=existing_active.completed_at,
                answers=existing_active.answers or {},
                total_score=float(existing_active.total_score or 0.0),
                max_score=float(existing_active.max_score or 100.0)
            )

    # Check candidate completed attempt count against max_attempts
    completed_count = db.query(ExamAttempt).filter(
        ExamAttempt.candidate_id == current_user.id,
        ExamAttempt.exam_id == exam.id,
        ExamAttempt.status.in_(["SUBMITTED", "COMPLETED"])
    ).count()

    if completed_count >= exam.max_attempts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Attempt limit reached. Maximum allowed attempts for this exam: {exam.max_attempts}."
        )

    expires = now + timedelta(minutes=exam.duration_minutes)

    new_attempt = ExamAttempt(
        candidate_id=current_user.id,
        exam_id=exam.id,
        status="STARTED",
        started_at=now,
        expires_at=expires,
        answers={},
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
        answers=new_attempt.answers or {},
        total_score=float(new_attempt.total_score or 0.0),
        max_score=float(new_attempt.max_score or 100.0)
    )

@router.get("/exams/{exam_id}/active-attempt", response_model=AttemptResponseSchema)
def get_active_attempt_for_exam(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves current active exam attempt for a candidate if present."""
    try:
        e_uuid = uuid.UUID(exam_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid exam_id UUID format.")

    exam = db.query(Exam).filter(Exam.id == e_uuid).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    if current_user.role == "candidate":
        require_candidate_exam_access(db, exam, current_user)

    now = datetime.utcnow()
    attempt = db.query(ExamAttempt).filter(
        ExamAttempt.candidate_id == current_user.id,
        ExamAttempt.exam_id == exam.id,
        ExamAttempt.status.in_(["STARTED", "IN_PROGRESS"])
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="No active exam attempt found.")

    exp = make_naive(attempt.expires_at)
    if now >= exp:
        attempt.status = "EXPIRED"
        db.commit()
        raise HTTPException(status_code=400, detail="Exam attempt has expired.")

    remaining = max(int((exp - now).total_seconds()), 0)

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
        answers=attempt.answers or {},
        total_score=float(attempt.total_score or 0.0),
        max_score=float(attempt.max_score or 100.0)
    )

@router.get("/attempts/{attempt_id}", response_model=AttemptResponseSchema)
def get_attempt_by_id(
    attempt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves exam attempt state, saved answers, and remaining time.
    Strictly checks candidate ownership (attempt.candidate_id == current_user.id).
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

    now = datetime.utcnow()
    exp = make_naive(attempt.expires_at)
    if now >= exp and attempt.status in ["STARTED", "IN_PROGRESS"]:
        attempt.status = "EXPIRED"
        db.commit()

    remaining = max(int((exp - now).total_seconds()), 0)

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
        answers=attempt.answers or {},
        total_score=float(attempt.total_score or 0.0),
        max_score=float(attempt.max_score or 100.0)
    )

@router.get("/attempts/{attempt_id}/questions")
def get_attempt_questions_for_student(
    attempt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves examination-safe questions for a student taking an exam attempt.
    STRICT SECURITY REQUIREMENT:
    Omits correct_answer, explanation, step_by_step_solution, expected_output, solution, source_analysis.
    """
    try:
        a_uuid = uuid.UUID(attempt_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attempt_id UUID format.")

    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == a_uuid).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found.")

    if current_user.role == "candidate" and attempt.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only access your own exam attempt questions.")

    exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found for attempt.")

    if current_user.role == "candidate":
        require_candidate_exam_access(db, exam, current_user)

    # Fetch QuestionPaper if linked
    qp = db.query(QuestionPaper).filter(QuestionPaper.published_exam_id == exam.id).first()

    questions_list = []
    q_num = 1

    if qp and qp.sections:
        for s_idx, sec in enumerate(qp.sections):
            sec_type = sec.get("question_type", "MCQ").upper()
            for q_item in sec.get("questions", []):
                q_id = str(q_item.get("id") or f"q_{q_num}")
                clean_q = {
                    "id": q_id,
                    "question_id": q_id,
                    "number": q_item.get("number", q_num),
                    "question": q_item.get("question") or q_item.get("title") or "",
                    "title": q_item.get("question") or q_item.get("title") or "",
                    "description": q_item.get("question") or q_item.get("description") or "",
                    "question_type": sec_type,
                    "section_name": sec.get("name", f"Section {s_idx + 1}"),
                    "options": q_item.get("options", []),
                    "marks": float(q_item.get("marks", 10.0)),
                    "max_score": float(q_item.get("marks", 10.0))
                }
                # STRICT EXCLUSIONS: Guarantee no solutions/answers leak
                clean_q.pop("correct_answer", None)
                clean_q.pop("explanation", None)
                clean_q.pop("solution", None)
                clean_q.pop("step_by_step_solution", None)
                clean_q.pop("expected_output", None)
                questions_list.append(clean_q)
                q_num += 1
    else:
        # Fallback to dim_questions
        db_qs = db.query(Question).filter(Question.exam_id == exam.id, Question.is_active == True).order_by(Question.question_order).all()
        for db_q in db_qs:
            questions_list.append({
                "id": str(db_q.id),
                "question_id": str(db_q.id),
                "number": db_q.question_order,
                "question": db_q.description or db_q.title,
                "title": db_q.title,
                "description": db_q.description,
                "question_type": "SHORT_ANSWER",
                "options": [],
                "marks": float(db_q.max_score),
                "max_score": float(db_q.max_score)
            })

    return {
        "attempt_id": str(attempt.id),
        "exam_id": str(exam.id),
        "title": exam.title,
        "class_level": exam.class_level,
        "subject": exam.subject,
        "language": exam.language,
        "duration_minutes": exam.duration_minutes,
        "maximum_marks": float(exam.max_score),
        "total_questions": len(questions_list),
        "questions": questions_list
    }

@router.put("/attempts/{attempt_id}/answers", response_model=AttemptResponseSchema)
def autosave_attempt_answers(
    attempt_id: str,
    payload: AnswerSaveSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Autosaves candidate answers for an active attempt into fact_exam_attempts.answers (JSONB).
    IDOR Protection: Strictly verifies attempt.candidate_id == current_user.id.
    Prevents modifying answers on locked/finished/expired attempts.
    """
    try:
        a_uuid = uuid.UUID(attempt_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attempt_id UUID format.")

    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == a_uuid).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found.")

    if attempt.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only update answers for your own attempt.")

    exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found for attempt.")

    if current_user.role == "candidate":
        require_candidate_exam_access(db, exam, current_user)

    if attempt.status in ["SUBMITTED", "COMPLETED", "EXPIRED", "CANCELLED"]:
        raise HTTPException(status_code=400, detail=f"Cannot update answers: Attempt is already {attempt.status.lower()}.")

    now = datetime.utcnow()
    exp = make_naive(attempt.expires_at)
    if now >= exp:
        attempt.status = "EXPIRED"
        db.commit()
        raise HTTPException(status_code=400, detail="Cannot update answers: Exam attempt time has expired.")

    # Merge answers dictionary
    current_answers = dict(attempt.answers or {})
    current_answers.update(payload.answers)
    attempt.answers = current_answers

    db.commit()
    db.refresh(attempt)

    remaining = max(int((exp - now).total_seconds()), 0)

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
        answers=attempt.answers or {},
        total_score=float(attempt.total_score or 0.0),
        max_score=float(attempt.max_score or 100.0)
    )

@router.post("/attempts/{attempt_id}/submit", response_model=AttemptResponseSchema)
def submit_exam_attempt(
    attempt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submits the exam attempt, locks answers, and triggers Multi-Agent Evaluation Engine.
    Enforces duplicate submission protection.
    """
    try:
        a_uuid = uuid.UUID(attempt_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attempt_id UUID format.")

    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == a_uuid).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found.")

    if attempt.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only submit your own exam attempt.")

    exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found for attempt.")

    if current_user.role == "candidate":
        require_candidate_exam_access(db, exam, current_user)

    if attempt.status in ["SUBMITTED", "COMPLETED"]:
        raise HTTPException(status_code=400, detail="Duplicate submission rejected: Exam attempt has already been submitted.")

    now = datetime.utcnow()
    attempt.status = "SUBMITTED"
    attempt.submitted_at = now
    db.commit()
    db.refresh(attempt)

    # Automatically trigger Multi-Agent Evaluation Engine
    eval_res = evaluate_attempt_service(db, attempt)

    db.refresh(attempt)

    exp = make_naive(attempt.expires_at)
    remaining = max(int((exp - now).total_seconds()), 0)

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
        answers=attempt.answers or {},
        total_score=float(attempt.total_score or 0.0),
        max_score=float(attempt.max_score or 100.0)
    )

@router.get("/attempts/{attempt_id}/result")
def get_attempt_result(
    attempt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves evaluation result for an exam attempt.
    Student access: Can only view their own result (returns examination-safe summary without secret teacher keys).
    Teacher access: Can only view results for exams they own/manage (returns full evaluation breakdown).
    """
    try:
        a_uuid = uuid.UUID(attempt_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attempt_id UUID format.")

    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == a_uuid).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found.")

    exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found for attempt.")

    # Candidate access authorization
    if current_user.role == "candidate":
        if attempt.candidate_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden: You can only access your own evaluation result.")

    # Recruiter/Teacher access authorization
    elif current_user.role in ["recruiter", "teacher"]:
        if current_user.role != "admin" and exam.created_by is not None and exam.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden: You do not own this exam.")

    eval_record = db.query(ExamEvaluation).filter(ExamEvaluation.attempt_id == attempt.id).first()
    if not eval_record:
        # Auto-trigger evaluation if attempt was submitted but not evaluated
        if attempt.status in ["SUBMITTED", "COMPLETED"]:
            eval_record = evaluate_attempt_service(db, attempt)
        else:
            raise HTTPException(status_code=404, detail="No evaluation result found. Exam attempt has not been submitted.")

    # Format response based on user role
    if current_user.role == "candidate":
        # Candidate View: Examination-safe summary
        saved_answers = dict(attempt.answers or {})
        cleaned_questions = []
        for q_res in (eval_record.question_results or []):
            cleaned_questions.append({
                "question_id": q_res.get("question_id"),
                "number": q_res.get("number"),
                "question": q_res.get("question"),
                "question_type": q_res.get("question_type"),
                "user_answer": q_res.get("user_answer"),
                "awarded_marks": q_res.get("awarded_marks"),
                "maximum_marks": q_res.get("maximum_marks"),
                "correctness": q_res.get("correctness")
            })

        return {
            "attempt_id": str(attempt.id),
            "exam_id": str(exam.id),
            "title": exam.title,
            "class_level": exam.class_level,
            "subject": exam.subject,
            "status": eval_record.status,
            "total_score": float(eval_record.total_score),
            "maximum_score": float(eval_record.maximum_score),
            "percentage": float(eval_record.percentage),
            "grade": eval_record.grade,
            "completed_at": eval_record.completed_at.isoformat() if eval_record.completed_at else None,
            "total_questions": len(cleaned_questions),
            "answered_questions": len(saved_answers),
            "question_summary": cleaned_questions
        }
    else:
        # Teacher View: Full evaluation breakdown with agent metadata & findings
        cand_user = db.query(User).filter(User.id == eval_record.candidate_id).first()
        return {
            "id": str(eval_record.id),
            "attempt_id": str(eval_record.attempt_id),
            "exam_id": str(eval_record.exam_id),
            "candidate_id": str(eval_record.candidate_id),
            "candidate_email": cand_user.email if cand_user else "Unknown",
            "status": eval_record.status,
            "total_score": float(eval_record.total_score),
            "maximum_score": float(eval_record.maximum_score),
            "percentage": float(eval_record.percentage),
            "grade": eval_record.grade,
            "question_results": eval_record.question_results,
            "evaluator_metadata": eval_record.evaluator_metadata,
            "error_message": eval_record.error_message,
            "started_at": eval_record.started_at.isoformat() if eval_record.started_at else None,
            "completed_at": eval_record.completed_at.isoformat() if eval_record.completed_at else None
        }

@router.post("/attempts/{attempt_id}/evaluate")
def evaluate_attempt_endpoint(
    attempt_id: str,
    payload: Optional[EvaluationRetryRequestSchema] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually triggers or retries evaluation for an exam attempt.
    """
    try:
        a_uuid = uuid.UUID(attempt_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attempt_id UUID format.")

    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == a_uuid).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found.")

    exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found for attempt.")

    if current_user.role == "candidate" and attempt.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only evaluate your own exam attempt.")

    if current_user.role in ["recruiter", "teacher"] and current_user.role != "admin" and exam.created_by is not None and exam.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this exam.")

    force_recalc = payload.force_recalculate if payload else False
    eval_record = evaluate_attempt_service(db, attempt, force_recalculate=force_recalc)

    return {
        "id": str(eval_record.id),
        "attempt_id": str(eval_record.attempt_id),
        "exam_id": str(eval_record.exam_id),
        "candidate_id": str(eval_record.candidate_id),
        "status": eval_record.status,
        "total_score": float(eval_record.total_score),
        "maximum_score": float(eval_record.maximum_score),
        "percentage": float(eval_record.percentage),
        "grade": eval_record.grade,
        "question_results": eval_record.question_results,
        "error_message": eval_record.error_message,
        "completed_at": eval_record.completed_at.isoformat() if eval_record.completed_at else None
    }

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
        answers=attempt.answers or {},
        total_score=float(attempt.total_score or 0.0),
        max_score=float(attempt.max_score or 100.0)
    )
