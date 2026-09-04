import io
import uuid
import logging
from typing import List, Dict, Any, Optional

try:
    import pypdf
except ImportError:
    pypdf = None
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import User, QuestionPaper, Exam, Question, TestCase
from app.api.auth import get_current_user
from app.ai.question_generator import generate_ai_question_paper
from app.ai.provider import get_question_generator_provider


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/question-papers",
    tags=["AI Question Paper Generator"],
)


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class SectionConfigSchema(BaseModel):
    name: str = Field(default="Section A")
    question_type: str = Field(default="MCQ")
    num_questions: int = Field(default=5, ge=1, le=100)
    marks_per_question: float = Field(default=2.0, gt=0)


class GeneratePaperRequest(BaseModel):
    class_level: int = Field(..., ge=1, le=12)
    subject: str = Field(..., min_length=1)
    topic: Optional[str] = Field(default="")
    exact_topic: Optional[str] = None
    source_type: str = Field(default="TOPIC_ONLY")  # TOPIC_ONLY, PDF_ONLY, PDF_AND_TOPIC
    source_document_id: Optional[str] = None
    source_context: Optional[str] = None
    language: str = Field(default="English")
    difficulty: str = Field(default="medium")
    duration_minutes: int = Field(default=60, gt=0)
    maximum_marks: float = Field(default=100.0, gt=0)
    sections: List[SectionConfigSchema]


class AnalyzeTopicRequest(BaseModel):
    class_level: int = Field(..., ge=1, le=12)
    subject: str = Field(..., min_length=1)
    topic: str = Field(..., min_length=1)
    language: str = Field(default="English")


class AnalyzeTopicResponse(BaseModel):
    class_level: int
    subject: str
    language: str
    topic: str
    key_concepts: List[str]
    question_areas: List[str]
    learning_objectives: List[str]
    recommended_difficulty: str
    suggested_duration: int
    suggested_marks: float


class AnalyzePdfResponse(BaseModel):
    document_id: str
    filename: str
    page_count: int
    source_context: str
    key_concepts: List[str]
    suggested_topics: List[str]
    summary: str


class SaveQuestionPaperRequest(BaseModel):
    title: str
    class_level: int = Field(..., ge=1, le=12)
    subject: str
    topic: str
    exact_topic: Optional[str] = None
    source_type: Optional[str] = "TOPIC_ONLY"
    source_document_id: Optional[str] = None
    source_context: Optional[str] = None
    language: str = "English"
    difficulty: str = "medium"
    duration_minutes: int = 60
    maximum_marks: float = 100.0
    status: str = "DRAFT"
    instructions: str = (
        "1. Answer all questions.\n"
        "2. Show steps where required."
    )
    sections: List[Dict[str, Any]]


# ============================================================================
# HELPERS
# ============================================================================

def require_educator(current_user: User) -> None:
    """Allow only teachers/recruiters and administrators."""

    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Educator or Admin role required.",
        )


def verify_question_paper_owner(
    qp: QuestionPaper,
    current_user: User,
) -> None:
    """
    Ensure teachers can only modify their own question papers.
    Admins can access all papers.
    """

    if current_user.role == "admin":
        return

    if qp.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: You do not own this question paper.",
        )


def build_paper_title(
    class_level: int,
    subject: str,
    topic: str,
    language: str,
) -> tuple[str, str]:
    """Generates an appropriate title and instructions based on parameters."""

    if language.lower() == "kannada" or "ಕನ್ನಡ" in topic:
        title = f"ತರಗತಿ {class_level} {subject} — {topic} ಪರೀಕ್ಷೆ"
        instructions = (
            "1. ಎಲ್ಲಾ ಪ್ರಶ್ನೆಗಳಿಗೂ ಕಡ್ಡಾಯವಾಗಿ ಉತ್ತರಿಸಿ.\n"
            "2. ಅಗತ್ಯವಿರುವ ಕಡೆ ಹಂತ-ಹಂತದ ಉತ್ತರ ಅಥವಾ ವಿವರಣೆಯನ್ನು ಬರೆಯಿರಿ.\n"
            "3. ಪ್ರತಿಯೊಂದು ಪ್ರಶ್ನೆಯನ್ನು ಗಮನವಿಟ್ಟು ಓದಿ."
        )
    else:
        title = f"Class {class_level} {subject} — {topic} Assessment"
        instructions = (
            "1. Answer all questions carefully.\n"
            "2. Show step-by-step mathematical derivations or reasoning where required.\n"
            "3. Ensure all final numerical values are clearly highlighted."
        )

    return title, instructions


# ============================================================================
# 1. ANALYZE TOPIC
# ============================================================================

@router.post("/analyze-topic", response_model=AnalyzeTopicResponse)
def analyze_topic_endpoint(
    req: AnalyzeTopicRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyzes a topic and suggests structure for question generation."""

    require_educator(current_user)

    if req.language.lower() == "kannada" or "ಕನ್ನಡ" in req.topic:
        key_concepts = [
            f"{req.topic} ವಿಷಯದ ಮೂಲ ಪರಿಕಲ್ಪನೆಗಳು",
            f"ತರಗತಿ {req.class_level} ಮಟ್ಟಕ್ಕೆ ಸೂಕ್ತವಾದ ನಿಯಮಗಳು",
            f"{req.topic} ಉದಾಹರಣೆಗಳ ವಿಶ್ಲೇಷಣೆ",
            "ಅನ್ವಯಿಕ ಜ್ಞಾನ ಮತ್ತು ಸಮಸ್ಯೆ ಪರಿಹಾರ",
        ]
        question_areas = [
            f"{req.topic} ಮೂಲ ಪರಿಕಲ್ಪನೆಗಳು",
            "ಬಹು ಆಯ್ಕೆ ಪ್ರಶ್ನೆಗಳು",
            "ಸಣ್ಣ ಉತ್ತರ ಪ್ರಶ್ನೆಗಳು",
            "ಅನ್ವಯಿಕ ಮತ್ತು ವಿವರಣಾತ್ಮಕ ಪ್ರಶ್ನೆಗಳು",
        ]
        learning_objectives = [
            f"ತರಗತಿ {req.class_level} ಪಠ್ಯಕ್ರಮದ ಅರಿವು",
            f"{req.topic} ಸರಿಯಾದ ಅನ್ವಯ",
            "ಸಮಸ್ಯೆ ಪರಿಹಾರ ಮತ್ತು ತಾರ್ಕಿಕ ಚಿಂತನೆ",
        ]
    else:
        key_concepts = [
            f"Core principles of {req.topic}",
            f"Class {req.class_level} curriculum concepts",
            f"Examples and applications of {req.topic}",
            "Problem solving and analytical reasoning",
        ]
        question_areas = [
            f"Fundamental concepts of {req.topic}",
            "Analytical multiple-choice questions",
            "Application-based questions",
            "Step-by-step problem solving",
        ]
        learning_objectives = [
            f"Master {req.topic} at Class {req.class_level} level",
            "Apply concepts correctly",
            "Develop problem-solving and critical-thinking skills",
        ]

    return AnalyzeTopicResponse(
        class_level=req.class_level,
        subject=req.subject,
        language=req.language,
        topic=req.topic,
        key_concepts=key_concepts,
        question_areas=question_areas,
        learning_objectives=learning_objectives,
        recommended_difficulty="medium",
        suggested_duration=60,
        suggested_marks=50.0,
    )


# ============================================================================
# 1B. ANALYZE PDF DOCUMENT
# ============================================================================

@router.post("/analyze-pdf", response_model=AnalyzePdfResponse)
async def analyze_pdf_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Parse uploaded PDF file, extract text context and key topics."""

    require_educator(current_user)

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only PDF files are supported.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    try:
        reader = pypdf.PdfReader(io.BytesIO(content))
        page_count = len(reader.pages)
        extracted_pages = []
        for idx, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            if txt.strip():
                extracted_pages.append(f"--- Page {idx + 1} ---\n{txt.strip()}")

        raw_text = "\n\n".join(extracted_pages).strip()
        if not raw_text:
            raw_text = f"PDF Document '{file.filename}' content parsed."
    except Exception as exc:
        logger.warning("PDF extraction error for %s: %s", file.filename, exc)
        raw_text = f"PDF Document '{file.filename}' loaded."
        page_count = 1

    doc_id = f"pdf-{uuid.uuid4().hex[:8]}"

    words = [w.strip() for w in raw_text.split() if len(w.strip()) > 3]
    capitalized = list(dict.fromkeys([w for w in words if w[0].isupper() and w.isalpha()]))[:6]

    key_concepts = capitalized if capitalized else [f"Concepts in {file.filename}"]
    suggested_topics = capitalized[:3] if len(capitalized) >= 2 else [file.filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title()]

    summary = (
        f"Uploaded PDF document '{file.filename}' with {page_count} page(s). "
        f"Parsed {len(raw_text)} characters of educational source text."
    )

    return AnalyzePdfResponse(
        document_id=doc_id,
        filename=file.filename,
        page_count=page_count,
        source_context=raw_text[:6000],
        key_concepts=key_concepts,
        suggested_topics=suggested_topics,
        summary=summary,
    )


# ============================================================================
# 1C. GENERATE QUESTION PAPER
# ============================================================================

@router.post("/generate")
def generate_question_paper_endpoint(
    req: GeneratePaperRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate an AI-powered question paper with solutions."""

    require_educator(current_user)

    effective_topic = (req.exact_topic or req.topic or "").strip()
    if not effective_topic:
        if req.source_type == "PDF_ONLY":
            effective_topic = "PDF Content"
        else:
            effective_topic = "General Subject Topic"

    sec_dicts = [s.dict() for s in req.sections]
    total_requested = sum(int(s["num_questions"]) for s in sec_dicts)

    if total_requested < 1:
        raise HTTPException(
            status_code=400,
            detail="Question count must be at least 1.",
        )
    if total_requested > 100:
        raise HTTPException(
            status_code=400,
            detail="Question count cannot exceed 100.",
        )

    ai_provider = get_question_generator_provider()
    provider_name = getattr(ai_provider, "provider_name", "AI") if ai_provider else None

    if ai_provider is not None:
        try:
            logger.info(
                "Starting %s question generation (Mode: %s): Class=%s Subject=%s Topic='%s' Language=%s",
                provider_name,
                req.source_type,
                req.class_level,
                req.subject,
                effective_topic,
                req.language,
            )

            generated_sections = []
            question_counter = 1

            for section in sec_dicts:
                num_questions = int(section["num_questions"])
                marks_per_question = float(section["marks_per_question"])
                question_type = section.get("question_type", "MCQ")

                result = ai_provider.generate_questions(
                    class_level=req.class_level,
                    subject=req.subject,
                    topic=effective_topic,
                    language=req.language,
                    difficulty=req.difficulty,
                    question_type=question_type,
                    num_questions=num_questions,
                    marks_per_question=marks_per_question,
                    source_type=req.source_type,
                    source_context=req.source_context,
                    exact_topic=req.exact_topic or effective_topic,
                )

                section_questions = []
                for question in result["questions"]:
                    question["number"] = question_counter
                    section_questions.append(question)
                    question_counter += 1

                section_total_marks = num_questions * marks_per_question
                generated_sections.append({
                    "name": section.get("name", "Section"),
                    "question_type": question_type,
                    "num_questions": num_questions,
                    "marks_per_question": marks_per_question,
                    "section_total_marks": section_total_marks,
                    "questions": section_questions,
                })

            title, instructions = build_paper_title(
                class_level=req.class_level,
                subject=req.subject,
                topic=effective_topic,
                language=req.language,
            )

            paper_dict = {
                "title": title,
                "class_level": req.class_level,
                "subject": req.subject,
                "language": (
                    "Kannada"
                    if req.language.lower() == "kannada"
                    else "English"
                ),
                "topic": effective_topic,
                "exact_topic": req.exact_topic or effective_topic,
                "source_type": req.source_type,
                "source_document_id": req.source_document_id,
                "source_context": req.source_context,
                "difficulty": req.difficulty,
                "duration_minutes": req.duration_minutes,
                "maximum_marks": req.maximum_marks,
                "instructions": instructions,
                "sections": generated_sections,
                "generation_provider": provider_name,
            }

            logger.info(
                "%s successfully generated %s questions (Mode: %s).",
                provider_name,
                question_counter - 1,
                req.source_type,
            )

            return paper_dict

        except Exception as exc:
            logger.error("%s generation failed: %s", provider_name, exc)
            raise HTTPException(
                status_code=503,
                detail="AI generation is temporarily unavailable. Please try again.",
            )

    # --------------------------------------------------------
    # Deterministic fallback (Explicit dev mode only)
    # --------------------------------------------------------

    logger.info(
        "Using deterministic question generator fallback."
    )

    paper_dict = generate_ai_question_paper(
        class_level=req.class_level,
        subject=req.subject,
        topic=effective_topic,
        language=req.language,
        difficulty=req.difficulty,
        duration_minutes=req.duration_minutes,
        maximum_marks=req.maximum_marks,
        sections_config=sec_dicts,
    )
    paper_dict["source_type"] = req.source_type
    paper_dict["exact_topic"] = req.exact_topic or effective_topic
    paper_dict["source_document_id"] = req.source_document_id
    paper_dict["source_context"] = req.source_context

    # --------------------------------------------------------
    # Validate total questions count
    # --------------------------------------------------------
    expected_total_questions = sum(
        int(section["num_questions"])
        for section in sec_dicts
    )

    if expected_total_questions < 1:
        raise HTTPException(
            status_code=400,
            detail="Question count must be at least 1.",
        )

    if expected_total_questions > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 questions allowed per paper.",
        )

    paper_dict["generation_provider"] = (
        "DETERMINISTIC_FALLBACK"
    )

    actual_total_questions = sum(
        len(section.get("questions", []))
        for section in paper_dict.get("sections", [])
    )

    if actual_total_questions != expected_total_questions:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Question generation returned {actual_total_questions} "
                f"of {expected_total_questions} requested questions. Please try again."
            ),
        )

    return paper_dict


# ============================================================================
# 2. SAVE QUESTION PAPER
# ============================================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def save_question_paper_draft(
    req: SaveQuestionPaperRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a generated question paper."""

    require_educator(current_user)

    qp = QuestionPaper(
        title=req.title,
        class_level=req.class_level,
        subject=req.subject,
        language=req.language,
        topic=req.topic,
        exact_topic=req.exact_topic,
        source_type=req.source_type,
        source_document_id=req.source_document_id,
        source_context=req.source_context,
        difficulty=req.difficulty,
        duration_minutes=req.duration_minutes,
        maximum_marks=req.maximum_marks,
        status=req.status,
        instructions=req.instructions,
        sections=req.sections,
        created_by=current_user.id,
    )

    db.add(qp)
    db.commit()
    db.refresh(qp)

    return {
        "message": "Question paper saved successfully.",
        "id": str(qp.id),
    }


# ============================================================================
# 3. LIST QUESTION PAPERS
# ============================================================================

@router.get("")
def list_question_papers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List question papers created by the current teacher."""

    require_educator(current_user)

    query = db.query(QuestionPaper)

    if current_user.role != "admin":
        query = query.filter(
            QuestionPaper.created_by == current_user.id
        )

    qps = (
        query
        .order_by(QuestionPaper.created_at.desc())
        .all()
    )

    return [
        {
            "id": str(qp.id),
            "title": qp.title,
            "class_level": qp.class_level,
            "subject": qp.subject,
            "language": qp.language,
            "topic": qp.topic,
            "difficulty": qp.difficulty,
            "duration_minutes": qp.duration_minutes,
            "maximum_marks": float(qp.maximum_marks),
            "status": qp.status,
            "published_exam_id": (
                str(qp.published_exam_id)
                if qp.published_exam_id
                else None
            ),
            "created_at": qp.created_at.isoformat(),
        }
        for qp in qps
    ]


# ============================================================================
# 4. GET QUESTION PAPER
# ============================================================================

@router.get("/{paper_id}")
def get_question_paper_by_id(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get one question paper."""

    require_educator(current_user)

    qp = (
        db.query(QuestionPaper)
        .filter(QuestionPaper.id == paper_id)
        .first()
    )

    if not qp:
        raise HTTPException(
            status_code=404,
            detail="Question paper not found.",
        )

    verify_question_paper_owner(qp, current_user)

    return {
        "id": str(qp.id),
        "title": qp.title,
        "class_level": qp.class_level,
        "subject": qp.subject,
        "language": qp.language,
        "topic": qp.topic,
        "difficulty": qp.difficulty,
        "duration_minutes": qp.duration_minutes,
        "maximum_marks": float(qp.maximum_marks),
        "status": qp.status,
        "instructions": qp.instructions,
        "sections": qp.sections,
        "published_exam_id": (
            str(qp.published_exam_id)
            if qp.published_exam_id
            else None
        ),
        "created_at": qp.created_at.isoformat(),
    }


# ============================================================================
# 5. UPDATE QUESTION PAPER
# ============================================================================

@router.put("/{paper_id}")
def update_question_paper(
    paper_id: str,
    req: SaveQuestionPaperRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing question paper."""

    require_educator(current_user)

    qp = (
        db.query(QuestionPaper)
        .filter(QuestionPaper.id == paper_id)
        .first()
    )

    if not qp:
        raise HTTPException(
            status_code=404,
            detail="Question paper not found.",
        )

    verify_question_paper_owner(qp, current_user)

    qp.title = req.title
    qp.class_level = req.class_level
    qp.subject = req.subject
    qp.language = req.language
    qp.topic = req.topic
    qp.difficulty = req.difficulty
    qp.duration_minutes = req.duration_minutes
    qp.maximum_marks = req.maximum_marks
    qp.status = req.status
    qp.instructions = req.instructions
    qp.sections = req.sections

    db.commit()
    db.refresh(qp)

    return {
        "message": "Question paper updated successfully.",
        "id": str(qp.id),
    }


# ============================================================================
# 6. DELETE QUESTION PAPER
# ============================================================================

@router.delete("/{paper_id}")
def delete_question_paper(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a question paper."""

    require_educator(current_user)

    qp = (
        db.query(QuestionPaper)
        .filter(QuestionPaper.id == paper_id)
        .first()
    )

    if not qp:
        raise HTTPException(
            status_code=404,
            detail="Question paper not found.",
        )

    verify_question_paper_owner(qp, current_user)

    db.delete(qp)
    db.commit()

    return {
        "message": "Question paper deleted successfully."
    }


# ============================================================================
# 7. PUBLISH QUESTION PAPER
# ============================================================================

@router.post("/{paper_id}/publish")
def publish_question_paper(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Convert a QuestionPaper into an official Exam.

    Publishing does NOT assign the exam to students.
    Assignment remains a separate operation.
    """

    require_educator(current_user)

    qp = (
        db.query(QuestionPaper)
        .filter(QuestionPaper.id == paper_id)
        .first()
    )

    if not qp:
        raise HTTPException(
            status_code=404,
            detail="Question paper not found.",
        )

    verify_question_paper_owner(qp, current_user)

    # Prevent duplicate publishing.
    if qp.published_exam_id:
        return {
            "message": (
                "Question paper is already published."
            ),
            "question_paper_id": str(qp.id),
            "exam_id": str(qp.published_exam_id),
        }

    new_exam = Exam(
        title=qp.title,
        description=(
            f"[{qp.subject} | Class {qp.class_level} | "
            f"{qp.language}] {qp.topic} Examination"
        ),
        class_level=qp.class_level,
        subject=qp.subject,
        language=qp.language,
        difficulty=qp.difficulty,
        duration_minutes=qp.duration_minutes,
        max_score=qp.maximum_marks,
        max_attempts=1,
        is_active=True,
        is_published=True,
        created_by=current_user.id,
    )

    db.add(new_exam)
    db.flush()

    q_order = 1

    for section in (qp.sections or []):

        for q_item in section.get("questions", []):

            db_question = Question(
                exam_id=new_exam.id,
                title=(
                    f"Q{q_order}. "
                    f"{q_item.get('question', '')[:100]}"
                ),
                description=q_item.get(
                    "question",
                    "",
                ),
                difficulty=qp.difficulty,
                language=(
                    "python"
                    if "python" in qp.subject.lower()
                    else "text"
                ),
                max_score=q_item.get(
                    "marks",
                    10.0,
                ),
                question_order=q_order,
            )

            db.add(db_question)
            db.flush()

            # Preserve the existing database structure.
            # Student-facing exam flow can use these test cases.
            test_case = TestCase(
                question_id=db_question.id,
                test_case_order=1,
                input_data="1",
                expected_output=str(
                    q_item.get(
                        "correct_answer",
                        "A",
                    )
                ),
                is_hidden=False,
                weight=1.0,
            )

            db.add(test_case)

            q_order += 1

    qp.status = "PUBLISHED"
    qp.published_exam_id = new_exam.id

    db.commit()

    return {
        "message": (
            "Exam published successfully. "
            "Assign it to a class before it appears "
            "on the Student Portal."
        ),
        "question_paper_id": str(qp.id),
        "exam_id": str(new_exam.id),
    }


# ============================================================================
# 8. QUESTION PAPER PRINT VIEW
# ============================================================================

@router.get(
    "/{paper_id}/pdf",
    response_class=HTMLResponse,
)
def get_question_paper_html_pdf(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Printable question paper.

    Answers and solutions are intentionally excluded.
    """

    require_educator(current_user)

    qp = (
        db.query(QuestionPaper)
        .filter(QuestionPaper.id == paper_id)
        .first()
    )

    if not qp:
        raise HTTPException(
            status_code=404,
            detail="Question paper not found.",
        )

    verify_question_paper_owner(qp, current_user)

    sections_html = ""

    for section in (qp.sections or []):

        section_name = section.get(
            "name",
            "Section",
        )

        section_marks = section.get(
            "section_total_marks",
            0,
        )

        section_count = section.get(
            "num_questions",
            0,
        )

        questions_html = ""

        for question in section.get(
            "questions",
            [],
        ):

            options_html = ""

            options = question.get(
                "options",
                [],
            )

            if options:

                labels = ["A", "B", "C", "D"]

                option_items = ""

                for index, option in enumerate(options):

                    label = (
                        labels[index]
                        if index < len(labels)
                        else str(index + 1)
                    )

                    option_items += (
                        f"<div>"
                        f"<b>({label})</b> "
                        f"{option}"
                        f"</div>"
                    )

                options_html = (
                    "<div style='display:grid;"
                    "grid-template-columns:1fr 1fr;"
                    "gap:8px;"
                    "margin-top:8px;'>"
                    f"{option_items}"
                    "</div>"
                )

            questions_html += f"""
            <div style="
                margin-bottom:20px;
                page-break-inside:avoid;
            ">
                <div style="
                    font-weight:600;
                    font-size:14px;
                ">
                    Q{question.get('number', 1)}.
                    {question.get('question', '')}
                    <span style="
                        float:right;
                        font-size:12px;
                        color:#555;
                    ">
                        [{question.get('marks', 0)} Marks]
                    </span>
                </div>

                {options_html}
            </div>
            """

        sections_html += f"""
        <div style="
            margin-top:24px;
            border-top:2px solid #333;
            padding-top:12px;
        ">

            <h3 style="
                margin:0 0 12px 0;
                font-size:16px;
            ">
                {section_name}
                ({section_count} Questions ×
                {section.get('marks_per_question', 0)}
                Marks = {section_marks} Marks)
            </h3>

            {questions_html}

        </div>
        """

    formatted_instructions = (
        (qp.instructions or "")
        .replace("\n", "<br/>")
    )

    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>

        <meta charset="utf-8"/>

        <title>
            {qp.title} — Printable Question Paper
        </title>

        <link
            rel="stylesheet"
            href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css"
        />

        <script
            src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js">
        </script>

        <script
            src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js">
        </script>

        <style>

            body {{
                font-family:
                    'Segoe UI Historic',
                    'Noto Sans Kannada',
                    'Noto Sans',
                    Arial,
                    sans-serif;

                margin:40px;
                color:#111;
                line-height:1.6;
            }}

            .header {{
                text-align:center;
                border-bottom:2px solid #000;
                padding-bottom:16px;
                margin-bottom:24px;
            }}

            .title {{
                font-size:24px;
                font-weight:bold;
                margin-bottom:4px;
            }}

            .subtitle {{
                font-size:16px;
                font-weight:600;
                color:#444;
            }}

            .meta {{
                display:flex;
                justify-content:space-between;
                margin-top:12px;
                font-size:14px;
                font-weight:bold;
            }}

            .instructions {{
                background:#f8f9fa;
                border:1px solid #ddd;
                padding:12px;
                border-radius:6px;
                font-size:13px;
                margin-bottom:20px;
            }}

            @media print {{
                body {{
                    margin:20px;
                }}

                .no-print {{
                    display:none;
                }}
            }}

        </style>

    </head>

    <body>

        <button
            class="no-print"
            onclick="window.print()"
            style="
                float:right;
                padding:10px 20px;
                border:none;
                border-radius:6px;
                font-weight:bold;
                cursor:pointer;
            "
        >
            Print / Save as PDF
        </button>

        <div class="header">

            <div style="
                font-size:28px;
                font-weight:900;
            ">
                EduExam
            </div>

            <div class="title">
                CLASS {qp.class_level}
                — {qp.subject.upper()}
                ({qp.language.upper()})
            </div>

            <div class="subtitle">
                {qp.topic}
            </div>

            <div class="meta">
                <span>
                    Time Allowed:
                    {qp.duration_minutes} Minutes
                </span>

                <span>
                    Maximum Marks:
                    {float(qp.maximum_marks):.0f}
                </span>
            </div>

        </div>

        <div class="instructions">

            <strong>
                General Instructions:
            </strong>

            <br/>

            {formatted_instructions}

        </div>

        {sections_html}

        <script>

            document.addEventListener(
                "DOMContentLoaded",
                function() {{

                    renderMathInElement(
                        document.body,
                        {{
                            delimiters: [
                                {{
                                    left: "$$",
                                    right: "$$",
                                    display: true
                                }},
                                {{
                                    left: "\\\\[",
                                    right: "\\\\]",
                                    display: true
                                }},
                                {{
                                    left: "$",
                                    right: "$",
                                    display: false
                                }},
                                {{
                                    left: "\\\\(",
                                    right: "\\\\)",
                                    display: false
                                }}
                            ]
                        }}
                    );

                }}
            );

        </script>

    </body>
    </html>
    """

    return HTMLResponse(
        content=full_html
    )


# ============================================================================
# 9. ANSWER KEY
# ============================================================================

@router.get(
    "/{paper_id}/answer-key-pdf",
    response_class=HTMLResponse,
)
def get_answer_key_html_pdf(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Teacher-only printable answer key and solutions.
    """

    require_educator(current_user)

    qp = (
        db.query(QuestionPaper)
        .filter(QuestionPaper.id == paper_id)
        .first()
    )

    if not qp:
        raise HTTPException(
            status_code=404,
            detail="Question paper not found.",
        )

    verify_question_paper_owner(qp, current_user)

    solutions_html = ""

    for section in (qp.sections or []):

        section_name = section.get(
            "name",
            "Section",
        )

        section_questions_html = ""

        for question in section.get(
            "questions",
            [],
        ):

            raw_solution = (
                question.get(
                    "step_by_step_solution",
                    "",
                )
                or question.get(
                    "explanation",
                    "",
                )
            )

            formatted_solution = (
                raw_solution
                .replace("\n", "<br/>")
            )

            solutions_html += ""

            section_questions_html += f"""
            <div style="
                margin-bottom:24px;
                padding:16px;
                border:1px solid #e2e8f0;
                border-radius:8px;
                background:#fafafa;
                page-break-inside:avoid;
            ">

                <div style="
                    font-weight:bold;
                    font-size:15px;
                ">
                    Q{question.get('number', 1)}.
                    {question.get('question', '')}
                </div>

                <div style="
                    margin-top:8px;
                    font-weight:bold;
                    font-size:14px;
                ">
                    Correct Answer:
                    {question.get('correct_answer', '')}
                </div>

                <div style="
                    margin-top:6px;
                    font-size:13px;
                ">
                    <b>Explanation:</b>
                    {question.get('explanation', '')}
                </div>

                <div style="
                    margin-top:10px;
                    padding:10px;
                    background:#ffffff;
                    border-left:4px solid #0284c7;
                    font-size:13px;
                ">
                    <b>
                        Step-by-Step Solution:
                    </b>

                    <br/>

                    {formatted_solution}
                </div>

            </div>
            """

        solutions_html += f"""
        <div style="margin-top:24px;">

            <h3 style="
                border-bottom:2px solid #0284c7;
                padding-bottom:6px;
            ">
                {section_name}
                — Solutions & Marking Scheme
            </h3>

            {section_questions_html}

        </div>
        """

    full_html = f"""
    <!DOCTYPE html>

    <html lang="en">

    <head>

        <meta charset="utf-8"/>

        <title>
            {qp.title} — Official Answer Key
        </title>

        <link
            rel="stylesheet"
            href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css"
        />

        <script
            src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js">
        </script>

        <script
            src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js">
        </script>

        <style>

            body {{
                font-family:
                    'Segoe UI Historic',
                    'Noto Sans Kannada',
                    'Noto Sans',
                    Arial,
                    sans-serif;

                margin:40px;
                color:#111;
                line-height:1.6;
            }}

            .header {{
                text-align:center;
                border-bottom:3px double #0284c7;
                padding-bottom:16px;
                margin-bottom:24px;
            }}

            .teacher-badge {{
                display:inline-block;
                padding:4px 12px;
                border-radius:20px;
                font-size:12px;
                font-weight:bold;
                margin-bottom:8px;
            }}

            .title {{
                font-size:22px;
                font-weight:bold;
            }}

            .subtitle {{
                font-size:15px;
                font-weight:600;
            }}

            @media print {{
                body {{
                    margin:20px;
                }}

                .no-print {{
                    display:none;
                }}
            }}

        </style>

    </head>

    <body>

        <button
            class="no-print"
            onclick="window.print()"
            style="
                float:right;
                padding:10px 20px;
                border:none;
                border-radius:6px;
                font-weight:bold;
                cursor:pointer;
            "
        >
            Print / Save Answer Key PDF
        </button>

        <div class="header">

            <div class="teacher-badge">
                TEACHER ONLY — CONFIDENTIAL ANSWER KEY
            </div>

            <div style="
                font-size:26px;
                font-weight:900;
            ">
                EduExam
            </div>

            <div class="title">
                CLASS {qp.class_level}
                {qp.subject.upper()}
                ({qp.language.upper()})
                — {qp.topic}
            </div>

            <div class="subtitle">
                Official Step-by-Step Marking Scheme & Solutions
            </div>

        </div>

        {solutions_html}

        <script>

            document.addEventListener(
                "DOMContentLoaded",
                function() {{

                    renderMathInElement(
                        document.body,
                        {{
                            delimiters: [
                                {{
                                    left: "$$",
                                    right: "$$",
                                    display: true
                                }},
                                {{
                                    left: "\\\\[",
                                    right: "\\\\]",
                                    display: true
                                }},
                                {{
                                    left: "$",
                                    right: "$",
                                    display: false
                                }},
                                {{
                                    left: "\\\\(",
                                    right: "\\\\)",
                                    display: false
                                }}
                            ]
                        }}
                    );

                }}
            );

        </script>

    </body>

    </html>
    """

    return HTMLResponse(
        content=full_html
    )