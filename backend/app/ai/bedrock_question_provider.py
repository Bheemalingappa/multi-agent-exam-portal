import json
import logging
from typing import Dict, Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.ai.question_provider import QuestionGeneratorProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class BedrockQuestionGeneratorProvider(QuestionGeneratorProvider):
    """
    AWS Bedrock provider for educational question generation.

    Generates structured questions for Classes 1-12 using:
    - Class level
    - Subject
    - Topic
    - Language
    - Difficulty
    - Question type
    """

    def __init__(self):
        self.region = getattr(
            settings,
            "AWS_REGION",
            "us-east-1",
        )

        self.model_id = getattr(
            settings,
            "BEDROCK_MODEL_ID",
            "us.amazon.nova-2-lite-v1:0",
        )

        self.client = boto3.client(
            "bedrock-runtime",
            region_name=self.region,
        )

        logger.info(
            "Bedrock question generator initialized: %s",
            self.model_id,
        )

    def health_check(self) -> bool:
        """
        Check whether the Bedrock client can be initialized.

        We intentionally do not invoke the model here because
        the AWS account may currently be unauthorized for
        Bedrock model invocation.
        """
        try:
            return self.client is not None
        except Exception:
            return False

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
    ) -> Dict[str, Any]:

        prompt = self._build_prompt(
            class_level=class_level,
            subject=subject,
            topic=topic,
            language=language,
            difficulty=difficulty,
            question_type=question_type,
            num_questions=num_questions,
            marks_per_question=marks_per_question,
        )

        try:
            response = self.client.converse(
                modelId=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt,
                            }
                        ],
                    }
                ],
                inferenceConfig={
                    "temperature": 0.3,
                    "maxTokens": 12000,
                },
            )

            text = self._extract_text(response)

            data = self._parse_json(text)

            return self._validate_response(
                data=data,
                class_level=class_level,
                subject=subject,
                topic=topic,
                language=language,
                difficulty=difficulty,
                question_type=question_type,
                num_questions=num_questions,
                marks_per_question=marks_per_question,
            )

        except (ClientError, BotoCoreError) as exc:
            logger.exception(
                "AWS Bedrock question generation failed: %s",
                exc,
            )
            raise

        except Exception as exc:
            logger.exception(
                "Unexpected Bedrock question generation error: %s",
                exc,
            )
            raise

    @staticmethod
    def _extract_text(response: Dict[str, Any]) -> str:
        """
        Extract text from a Bedrock Converse response.
        """

        output = response.get("output", {})
        message = output.get("message", {})
        content = message.get("content", [])

        texts = []

        for item in content:
            if isinstance(item, dict) and "text" in item:
                texts.append(item["text"])

        if not texts:
            raise ValueError(
                "Bedrock returned an empty response."
            )

        return "\n".join(texts).strip()

    @staticmethod
    def _parse_json(text: str) -> Dict[str, Any]:
        """
        Parse JSON returned by the model.

        Handles both:
            {...}

        and:

            ```json
            {...}
            ```
        """

        cleaned = text.strip()

        if cleaned.startswith("```"):
            lines = cleaned.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned = "\n".join(lines).strip()

            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()

        try:
            return json.loads(cleaned)

        except json.JSONDecodeError as exc:
            logger.error(
                "Bedrock returned invalid JSON: %s",
                cleaned[:2000],
            )

            raise ValueError(
                "Bedrock returned invalid JSON."
            ) from exc

    def _build_prompt(
        self,
        class_level: int,
        subject: str,
        topic: str,
        language: str,
        difficulty: str,
        question_type: str,
        num_questions: int,
        marks_per_question: float,
    ) -> str:

        if language.lower() == "kannada":
            language_instruction = """
Generate ALL educational content in Kannada.

Use natural Kannada appropriate for Indian school students.
Do not merely translate English questions word-for-word.
Use Kannada educational terminology correctly.
"""
        else:
            language_instruction = """
Generate ALL educational content in English.
"""

        return f"""
You are an expert Indian school examination question-paper generator.

Your task is to generate exactly {num_questions}
high-quality questions.

========================
EDUCATIONAL CONTEXT
========================

Class:
{class_level}

Subject:
{subject}

Topic:
{topic}

Language:
{language}

Difficulty:
{difficulty}

Question Type:
{question_type}

Marks Per Question:
{marks_per_question}

========================
STRICT REQUIREMENTS
========================

1. Every question MUST be directly related to the specified topic.

2. Do NOT generate generic questions.

3. Do NOT change the subject.

4. Do NOT change the class level.

5. Follow the appropriate Indian school curriculum level.

6. Questions must be educationally meaningful.

7. Do NOT repeat questions.

8. Avoid duplicate concepts where possible.

9. Questions should test different aspects of the topic.

10. For MCQs, provide exactly four options.

11. Exactly one MCQ option must be correct.

12. The correct answer must actually solve the question.

13. Explanations must match the question.

14. Step-by-step solutions must be correct.

15. For mathematics, verify all calculations.

16. Use LaTeX for mathematical expressions when useful.

17. Do not put the answer inside the question itself.

18. Do not generate questions from unrelated chapters.

19. Do not invent curriculum facts.

20. Respect the student's class level.

{language_instruction}

========================
CLASS LEVEL GUIDANCE
========================

Classes 1-3:
- Very simple vocabulary
- Basic concepts
- Simple recognition
- Simple counting/reasoning
- Age-appropriate examples

Classes 4-5:
- Elementary concepts
- Simple reasoning
- Basic application

Classes 6-8:
- Middle-school concepts
- Conceptual understanding
- Moderate reasoning
- Basic application problems

Classes 9-10:
- Secondary-school concepts
- Board-exam style questions
- Application and analytical reasoning
- Appropriate numerical problems

Classes 11-12:
- Senior-secondary concepts
- Advanced conceptual questions
- Numerical/application questions
- Higher-order reasoning

========================
TOPIC RESTRICTION
========================

The ONLY topic to test is:

"{topic}"

Every question must clearly test knowledge or application
of this topic.

Do not drift into unrelated chapters.

========================
MATHEMATICS RULE
========================

If the subject is Mathematics:

- Verify every numerical calculation.
- Make sure exactly one answer is correct.
- Make distractor options plausible but incorrect.
- Use proper mathematical notation.
- Use LaTeX when appropriate.
- Include a logically correct solution.

========================
OUTPUT
========================

Return ONLY valid JSON.

Do NOT return Markdown.

Do NOT return explanations outside the JSON.

Use exactly this structure:

{{
    "questions": [
        {{
            "number": 1,
            "question": "Question text",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "correct_answer": "A",
            "marks": {marks_per_question},
            "explanation": "Explanation",
            "step_by_step_solution": "Step-by-step solution"
        }}
    ]
}}

For non-MCQ questions:

"options": []

The complete answer must be placed in:

"correct_answer"

Generate exactly:

{num_questions}

questions.
"""

    @staticmethod
    def _validate_response(
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
            raise ValueError(
                "Bedrock response must be an object."
            )

        questions = data.get("questions")

        if not isinstance(questions, list):
            raise ValueError(
                "Bedrock response does not contain a "
                "'questions' list."
            )

        if len(questions) != num_questions:
            raise ValueError(
                f"Expected {num_questions} questions, "
                f"received {len(questions)}."
            )

        q_texts = [str(q.get("question", "")).strip().lower() for q in questions if isinstance(q, dict)]
        if len(set(q_texts)) != len(q_texts):
            raise ValueError("Duplicate questions detected in generated output.")

        validated_questions = []

        for index, question in enumerate(
            questions,
            start=1,
        ):

            if not isinstance(question, dict):
                raise ValueError(
                    f"Question {index} is invalid."
                )

            question_text = str(
                question.get("question", "")
            ).strip()

            if not question_text:
                raise ValueError(
                    f"Question {index} has no question text."
                )

            options = question.get(
                "options",
                [],
            )

            if not isinstance(options, list):
                raise ValueError(
                    f"Question {index} options must be a list."
                )

            if question_type.upper() == "MCQ":

                if len(options) != 4:
                    raise ValueError(
                        f"Question {index} must have "
                        f"exactly four options."
                    )

                correct_answer = str(
                    question.get(
                        "correct_answer",
                        "",
                    )
                ).strip().upper()

                if correct_answer not in {
                    "A",
                    "B",
                    "C",
                    "D",
                }:
                    raise ValueError(
                        f"Question {index} has invalid "
                        f"correct_answer: "
                        f"{correct_answer}"
                    )

            else:

                correct_answer = str(
                    question.get(
                        "correct_answer",
                        "",
                    )
                ).strip()

                if not correct_answer:
                    raise ValueError(
                        f"Question {index} has no answer."
                    )

            explanation = str(
                question.get(
                    "explanation",
                    "",
                )
            ).strip()

            solution = str(
                question.get(
                    "step_by_step_solution",
                    "",
                )
            ).strip()

            validated_questions.append(
                {
                    "number": index,
                    "question": question_text,
                    "options": options,
                    "correct_answer": correct_answer,
                    "marks": marks_per_question,
                    "explanation": explanation,
                    "step_by_step_solution": solution,
                }
            )

        return {
            "questions": validated_questions,
            "class_level": class_level,
            "subject": subject,
            "topic": topic,
            "language": language,
            "difficulty": difficulty,
            "question_type": question_type,
        }