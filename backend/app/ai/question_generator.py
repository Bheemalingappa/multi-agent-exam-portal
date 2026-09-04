"""
Deterministic fallback question generator.

This module intentionally does NOT contain the Gemini/Bedrock implementation.
AI providers live in separate provider modules.

The public function generate_ai_question_paper() is kept for backward
compatibility with the existing question_papers API.
"""

from typing import Any, Dict, List


def _make_fallback_question(
    question_number: int,
    class_level: int,
    subject: str,
    topic: str,
    language: str,
    difficulty: str,
    question_type: str,
    marks: float,
) -> Dict[str, Any]:

    if language.lower() == "kannada":
        question_text = (
            f"ಪ್ರಶ್ನೆ {question_number}: "
            f"ತರಗತಿ {class_level} {subject} ವಿಷಯದ "
            f"'{topic}' ಎಂಬ ನಿಖರ ವಿಷಯದ ಮುಖ್ಯ ಅಂಶವನ್ನು ವಿವರಿಸಿ."
        )

        if question_type.upper() == "MCQ":
            return {
                "number": question_number,
                "question_text": question_text,
                "options": [
                    "ಆಯ್ಕೆ A",
                    "ಆಯ್ಕೆ B",
                    "ಆಯ್ಕೆ C",
                    "ಆಯ್ಕೆ D",
                ],
                "correct_answer": "ಆಯ್ಕೆ A",
                "explanation": (
                    f"ಈ ಪ್ರಶ್ನೆಯು '{topic}' ಎಂಬ ನಿರ್ದಿಷ್ಟ ವಿಷಯಕ್ಕೆ ಸಂಬಂಧಿಸಿದೆ."
                ),
                "marks": marks,
            }

        return {
            "number": question_number,
            "question_text": question_text,
            "options": [],
            "correct_answer": "",
            "explanation": (
                f"ಈ ಪ್ರಶ್ನೆಯು '{topic}' ಎಂಬ ನಿರ್ದಿಷ್ಟ ವಿಷಯವನ್ನು ಪರೀಕ್ಷಿಸುತ್ತದೆ."
            ),
            "marks": marks,
        }

    question_text = (
        f"Question {question_number}: "
        f"Explain the main concept of the exact topic "
        f"'{topic}' for Class {class_level} {subject}."
    )

    if question_type.upper() == "MCQ":
        return {
            "number": question_number,
            "question_text": question_text,
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D",
            ],
            "correct_answer": "Option A",
            "explanation": (
                f"This fallback question is specifically associated "
                f"with the topic '{topic}'."
            ),
            "marks": marks,
        }

    return {
        "number": question_number,
        "question_text": question_text,
        "options": [],
        "correct_answer": "",
        "explanation": (
            f"This fallback question is specifically associated "
            f"with the topic '{topic}'."
        ),
        "marks": marks,
    }


def generate_ai_question_paper(
    class_level: int,
    subject: str,
    topic: str,
    language: str,
    difficulty: str,
    duration_minutes: int,
    maximum_marks: float,
    sections_config: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Backward-compatible deterministic fallback.

    IMPORTANT:
    This is only used when the configured AI provider is unavailable
    or fails. It is not intended to replace real LLM generation.
    """

    sections = []
    question_counter = 1

    normalized_language = (
        "Kannada"
        if language.lower() == "kannada"
        else "English"
    )

    for section in sections_config:
        section_name = section.get("name", "Section")
        question_type = section.get("question_type", "MCQ")
        num_questions = int(section.get("num_questions", 0))
        marks_per_question = float(
            section.get("marks_per_question", 1)
        )

        questions = []

        for _ in range(num_questions):
            question = _make_fallback_question(
                question_number=question_counter,
                class_level=class_level,
                subject=subject,
                topic=topic,
                language=language,
                difficulty=difficulty,
                question_type=question_type,
                marks=marks_per_question,
            )

            questions.append(question)
            question_counter += 1

        section_total_marks = (
            num_questions * marks_per_question
        )

        sections.append(
            {
                "name": section_name,
                "question_type": question_type,
                "num_questions": num_questions,
                "marks_per_question": marks_per_question,
                "section_total_marks": section_total_marks,
                "questions": questions,
            }
        )

    return {
        "title": (
            f"Class {class_level} {subject} "
            f"- {topic}"
        ),
        "class_level": class_level,
        "subject": subject,
        "language": normalized_language,
        "topic": topic,
        "difficulty": difficulty,
        "duration_minutes": duration_minutes,
        "maximum_marks": maximum_marks,
        "instructions": [
            "Answer all questions.",
            f"Questions are based on the topic: {topic}.",
        ],
        "sections": sections,
        "generation_provider": "DETERMINISTIC_FALLBACK",
    }