import uuid
from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import Question, TestCase, Exam, User
from app.api.auth import get_current_user
from app.api.student_access import require_candidate_exam_access
from app.schemas.question import (
    QuestionCreateSchema, QuestionUpdateSchema,
    CandidateQuestionResponseSchema, RecruiterQuestionResponseSchema,
    TestCaseCreateSchema, TestCaseUpdateSchema, TestCaseRecruiterResponseSchema
)

router = APIRouter(tags=["Question Bank & Test Cases"])

# -----------------------------------------------------------------------------
# QUESTION ENDPOINTS
# -----------------------------------------------------------------------------
@router.post("/exams/{exam_id}/questions", response_model=RecruiterQuestionResponseSchema, status_code=status.HTTP_201_CREATED)
def create_question_for_exam(
    exam_id: str,
    payload: QuestionCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a new question under an exam. Requires Recruiter or Admin role."""
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Recruiter or Admin access required.")

    try:
        e_uuid = uuid.UUID(exam_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid exam_id UUID format.")

    exam = db.query(Exam).filter(Exam.id == e_uuid).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    new_q = Question(
        exam_id=exam.id,
        title=payload.title,
        description=payload.description,
        difficulty=payload.difficulty,
        language=payload.language,
        time_limit_seconds=payload.time_limit_seconds,
        memory_limit_mb=payload.memory_limit_mb,
        max_score=payload.max_score,
        question_order=payload.question_order
    )

    db.add(new_q)
    db.commit()
    db.refresh(new_q)

    return RecruiterQuestionResponseSchema(
        id=str(new_q.id),
        exam_id=str(new_q.exam_id),
        title=new_q.title,
        description=new_q.description,
        difficulty=new_q.difficulty,
        language=new_q.language,
        time_limit_seconds=new_q.time_limit_seconds,
        memory_limit_mb=new_q.memory_limit_mb,
        max_score=float(new_q.max_score),
        question_order=new_q.question_order,
        is_active=new_q.is_active,
        created_at=new_q.created_at
    )

@router.get("/exams/{exam_id}/questions")
def list_questions_for_exam(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lists questions for an exam.
    Candidates receive CandidateQuestionResponseSchema (hiding expected outputs and test case details).
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

    questions = db.query(Question).filter(Question.exam_id == e_uuid, Question.is_active == True).order_by(Question.question_order).all()

    if current_user.role == "candidate":
        return [
            CandidateQuestionResponseSchema(
                id=str(q.id),
                exam_id=str(q.exam_id),
                title=q.title,
                description=q.description,
                difficulty=q.difficulty,
                language=q.language,
                time_limit_seconds=q.time_limit_seconds,
                memory_limit_mb=q.memory_limit_mb,
                max_score=float(q.max_score),
                question_order=q.question_order
            )
            for q in questions
        ]
    else:
        return [
            RecruiterQuestionResponseSchema(
                id=str(q.id),
                exam_id=str(q.exam_id),
                title=q.title,
                description=q.description,
                difficulty=q.difficulty,
                language=q.language,
                time_limit_seconds=q.time_limit_seconds,
                memory_limit_mb=q.memory_limit_mb,
                max_score=float(q.max_score),
                question_order=q.question_order,
                is_active=q.is_active,
                created_at=q.created_at
            )
            for q in questions
        ]

@router.get("/questions/{question_id}")
def get_question_by_id(
    question_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves single question. Candidates receive CandidateQuestionResponseSchema."""
    try:
        q_uuid = uuid.UUID(question_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid question_id UUID format.")

    q = db.query(Question).filter(Question.id == q_uuid).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")

    if current_user.role == "candidate":
        return CandidateQuestionResponseSchema(
            id=str(q.id),
            exam_id=str(q.exam_id),
            title=q.title,
            description=q.description,
            difficulty=q.difficulty,
            language=q.language,
            time_limit_seconds=q.time_limit_seconds,
            memory_limit_mb=q.memory_limit_mb,
            max_score=float(q.max_score),
            question_order=q.question_order
        )
    else:
        return RecruiterQuestionResponseSchema(
            id=str(q.id),
            exam_id=str(q.exam_id),
            title=q.title,
            description=q.description,
            difficulty=q.difficulty,
            language=q.language,
            time_limit_seconds=q.time_limit_seconds,
            memory_limit_mb=q.memory_limit_mb,
            max_score=float(q.max_score),
            question_order=q.question_order,
            is_active=q.is_active,
            created_at=q.created_at
        )

# -----------------------------------------------------------------------------
# TEST CASE ENDPOINTS (RECRUITER/ADMIN ONLY)
# -----------------------------------------------------------------------------
@router.post("/questions/{question_id}/test-cases", response_model=TestCaseRecruiterResponseSchema, status_code=status.HTTP_201_CREATED)
def create_test_case_for_question(
    question_id: str,
    payload: TestCaseCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a hidden or visible test case for a question. Requires Recruiter or Admin role."""
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Recruiter or Admin access required.")

    try:
        q_uuid = uuid.UUID(question_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid question_id UUID format.")

    question = db.query(Question).filter(Question.id == q_uuid).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    order_count = db.query(TestCase).filter(TestCase.question_id == question.id).count() + 1

    new_tc = TestCase(
        question_id=question.id,
        test_case_order=order_count,
        input_data=payload.input_data,
        expected_output=payload.expected_output,
        is_hidden=payload.is_hidden,
        weight=payload.weight,
        timeout_seconds=payload.timeout_seconds
    )

    db.add(new_tc)
    db.commit()
    db.refresh(new_tc)

    return TestCaseRecruiterResponseSchema(
        id=str(new_tc.id),
        question_id=str(new_tc.question_id),
        test_case_order=new_tc.test_case_order,
        input_data=new_tc.input_data,
        expected_output=new_tc.expected_output,
        is_hidden=new_tc.is_hidden,
        weight=float(new_tc.weight),
        timeout_seconds=new_tc.timeout_seconds
    )

@router.get("/questions/{question_id}/test-cases", response_model=List[TestCaseRecruiterResponseSchema])
def list_test_cases_for_question(
    question_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists all test cases for a question. RECRUITER OR ADMIN ONLY. Rejects candidate access with 403."""
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Candidates cannot inspect test case details.")

    try:
        q_uuid = uuid.UUID(question_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid question_id UUID format.")

    test_cases = db.query(TestCase).filter(TestCase.question_id == q_uuid).order_by(TestCase.test_case_order).all()

    return [
        TestCaseRecruiterResponseSchema(
            id=str(tc.id),
            question_id=str(tc.question_id),
            test_case_order=tc.test_case_order,
            input_data=tc.input_data,
            expected_output=tc.expected_output,
            is_hidden=tc.is_hidden,
            weight=float(tc.weight),
            timeout_seconds=tc.timeout_seconds
        )
        for tc in test_cases
    ]
