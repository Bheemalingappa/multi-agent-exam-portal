import json
import time
import logging
from typing import Dict, Any, Optional

from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.ai.question_provider import QuestionGeneratorProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiQuestionGeneratorProvider(QuestionGeneratorProvider):

    def __init__(self):
        api_key = settings.GEMINI_API_KEY or settings.LLM_API_KEY
        if not api_key:
            raise ValueError("No API key was provided. Please pass a valid API key.")
        self.client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=30000))
        self.model_name = settings.GEMINI_MODEL or "gemini-3.6-flash"
        self.provider_name = "GEMINI"

    def health_check(self) -> bool:
        return bool(settings.GEMINI_API_KEY or settings.LLM_API_KEY)

    def generate_questions(
        self,
        class_level: int,
        subject: str,
        topic: str,
        language: str,
        difficulty: str,
        question_type: str,
        num_questions: int,
        marks_per_question: float,
        source_type: str = "TOPIC_ONLY",
        source_context: Optional[str] = None,
        exact_topic: Optional[str] = None,
    ) -> Dict[str, Any]:

        effective_topic = (exact_topic or topic or "").strip()
        if not effective_topic and source_type == "PDF_ONLY":
            effective_topic = "PDF Educational Content"

        logger.info(
            f"Starting Gemini question generation (Mode: {source_type}) for {num_questions} {question_type} questions: "
            f"Class={class_level} Subject={subject} Topic='{effective_topic}' Language={language} Marks={marks_per_question}"
        )

        prompt = self._build_concise_prompt(
            class_level=class_level,
            subject=subject,
            topic=effective_topic,
            language=language,
            difficulty=difficulty,
            question_type=question_type,
            num_questions=num_questions,
            marks_per_question=marks_per_question,
            source_type=source_type,
            source_context=source_context,
            exact_topic=exact_topic,
        )

        max_retries = 3
        backoff_seconds = 1.0

        for attempt in range(1, max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )

                if not response or not response.text:
                    raise ValueError("Gemini returned empty response text.")

                raw_json = response.text.strip()
                if raw_json.startswith("```json"):
                    raw_json = raw_json[7:]
                if raw_json.startswith("```"):
                    raw_json = raw_json[3:]
                if raw_json.endswith("```"):
                    raw_json = raw_json[:-3]
                raw_json = raw_json.strip()

                data = json.loads(raw_json)
                validated = self._validate_response(
                    data=data,
                    class_level=class_level,
                    subject=subject,
                    topic=effective_topic,
                    language=language,
                    difficulty=difficulty,
                    question_type=question_type,
                    num_questions=num_questions,
                    marks_per_question=marks_per_question,
                )

                logger.info(f"Gemini successfully generated {len(validated['questions'])} questions (Mode: {source_type})")
                return validated

            except APIError as exc:
                code = getattr(exc, "code", None)
                if code in (400, 401, 403, 429):
                    logger.error(f"Non-retriable/Rate-limited Gemini API error ({code}): {exc}")
                    raise exc
                
                if attempt == max_retries:
                    logger.error(f"Gemini failed after {max_retries} attempts: {exc}")
                    raise exc

                sleep_time = min(backoff_seconds * (2 ** (attempt - 1)), 2.0)
                logger.warning(f"Transient Gemini API error (attempt {attempt}/{max_retries}, code={code}). Retrying in {sleep_time}s... Error: {exc}")
                time.sleep(sleep_time)

            except Exception as exc:
                logger.error(f"Gemini generation error on attempt {attempt}: {exc}")
                if attempt == max_retries:
                    raise exc
                time.sleep(backoff_seconds)

    def _build_concise_prompt(
        self,
        class_level: int,
        subject: str,
        topic: str,
        language: str,
        difficulty: str,
        question_type: str,
        num_questions: int,
        marks_per_question: float,
        source_type: str = "TOPIC_ONLY",
        source_context: Optional[str] = None,
        exact_topic: Optional[str] = None,
    ) -> str:
        lang_instruction = (
            "Generate ALL questions, options, explanations, and step-by-step solutions in natural Kannada."
            if (language.lower() == "kannada" or "ಕನ್ನಡ" in topic or "ಕನ್ನಡ" in subject)
            else "Generate ALL educational content in English."
        )

        effective_topic = (exact_topic or topic or "").strip()

        if source_type == "PDF_ONLY" and source_context:
            context_block = f"""
SOURCE MODE: PDF_ONLY
Educational Source Context (Extracted PDF Document):
\"\"\"
{source_context[:3500]}
\"\"\"

MODE RULES:
1. Analyze the provided PDF context carefully.
2. Generate NEW questions testing key educational concepts present in this PDF document.
3. Do NOT copy PDF questions verbatim. Do NOT copy long passages or full articles into the question text.
"""
        elif source_type == "PDF_AND_TOPIC" and source_context:
            context_block = f"""
SOURCE MODE: PDF_AND_TOPIC
Target Exact Topic to Test: "{effective_topic}"
Educational Source Context (PDF Document):
\"\"\"
{source_context[:3500]}
\"\"\"

MODE RULES:
1. The exact topic is "{effective_topic}". This defines WHAT must be tested.
2. The provided PDF context provides the educational source material and depth.
3. Generate NEW questions specifically testing "{effective_topic}" using the PDF as source material.
4. Do NOT generate questions on unrelated chapters or topics in the PDF.
5. Do NOT copy PDF text or questions verbatim.
"""
        else:
            context_block = f"""
SOURCE MODE: TOPIC_ONLY
Target Exact Topic: "{effective_topic}"

MODE RULES:
1. Generate NEW questions specifically testing the exact topic: "{effective_topic}".
2. Do NOT generate generic subject questions or broaden the topic to unrelated chapters.
"""

        return f"""
You are an expert Indian school examination question-paper generator.
Generate EXACTLY {num_questions} NEW, distinct, non-repeating questions.

Context:
Class: {class_level}
Subject: {subject}
Exact Topic: "{effective_topic}"
Language: {language}
Difficulty: {difficulty}
Question Type: {question_type}
Marks Per Question: {marks_per_question}

{context_block}

{lang_instruction}

STRICT CONSTRAINTS:
1. Generate EXACTLY {num_questions} questions. Do NOT return fewer or more questions.
2. Every question must be distinct and non-repeating.
3. For MCQ questions, provide exactly 4 distinct options (labeled A, B, C, D or listed in an array of 4 items), exactly 1 correct answer matching one option, a clear explanation, and a step-by-step solution.
4. Return ONLY valid JSON matching this schema:
{{
  "questions": [
    {{
      "number": 1,
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "A",
      "marks": {marks_per_question},
      "explanation": "Explanation for answer",
      "step_by_step_solution": "Step-by-step solution"
    }}
  ]
}}
For non-MCQ questions, set "options": [] and put the expected answer in "correct_answer".
"""

    def _validate_response(
        self,
        data: Dict[str, Any],
        class_level: int,
        subject: str,
        topic: str,
        language: str,
        difficulty: str,
        question_type: str,
        num_questions: int,
        marks_per_question: float,
    ) -> Dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError("Gemini response must be a JSON object.")
        questions = data.get("questions")
        if not isinstance(questions, list):
            raise ValueError("Gemini response does not contain a 'questions' list.")
        if len(questions) != num_questions:
            raise ValueError(f"Gemini returned {len(questions)} questions instead of requested {num_questions}.")

        q_texts = [str(q.get("question", "") or q.get("question_text", "")).strip().lower() for q in questions if isinstance(q, dict)]
        if len(set(q_texts)) != len(q_texts):
            raise ValueError("Duplicate questions detected in Gemini output.")

        validated_questions = []
        for idx, q in enumerate(questions, start=1):
            if not isinstance(q, dict):
                raise ValueError(f"Question {idx} is invalid.")
            q_text = str(q.get("question", "") or q.get("question_text", "")).strip()
            if not q_text:
                raise ValueError(f"Question {idx} has no question text.")

            options = q.get("options", [])
            if not isinstance(options, list):
                options = []

            if question_type.upper() == "MCQ":
                if len(options) != 4:
                    raise ValueError(f"Question {idx} must have exactly 4 options.")
                correct_answer = str(q.get("correct_answer", "")).strip()
                if correct_answer.upper() in {"A", "B", "C", "D"}:
                    correct_val = correct_answer.upper()
                else:
                    if correct_answer in options:
                        opt_idx = options.index(correct_answer)
                        correct_val = ["A", "B", "C", "D"][opt_idx]
                    else:
                        correct_val = "A"
            else:
                correct_val = str(q.get("correct_answer", "")).strip() or "See detailed solution below."

            expl = str(q.get("explanation", "")).strip() or f"Explanation for question {idx}."
            sol = str(q.get("step_by_step_solution", "")).strip() or expl

            validated_questions.append({
                "number": idx,
                "question": q_text,
                "options": options if question_type.upper() == "MCQ" else [],
                "correct_answer": correct_val,
                "marks": marks_per_question,
                "explanation": expl,
                "step_by_step_solution": sol
            })

        return {"questions": validated_questions}