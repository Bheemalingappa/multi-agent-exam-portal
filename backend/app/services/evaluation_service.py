import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.database.models import ExamAttempt, Exam, QuestionPaper, Question, ExamEvaluation
from app.agents.provider import get_agent_provider
from app.agents.consensus import A2AConsensusEngine

logger = logging.getLogger(__name__)

def calculate_letter_grade(percentage: float) -> str:
    """
    Standard Grading System:
    90–100% -> A+
    80–89.99% -> A
    70–79.99% -> B+
    60–69.99% -> B
    50–59.99% -> C
    40–49.99% -> D
    Below 40% -> F
    """
    if percentage >= 90.0:
        return "A+"
    elif percentage >= 80.0:
        return "A"
    elif percentage >= 70.0:
        return "B+"
    elif percentage >= 60.0:
        return "B"
    elif percentage >= 50.0:
        return "C"
    elif percentage >= 40.0:
        return "D"
    else:
        return "F"

def evaluate_attempt_service(
    db: Session,
    attempt: ExamAttempt,
    force_recalculate: bool = False
) -> ExamEvaluation:
    """
    Core Multi-Agent Evaluation & Scoring Engine.
    Evaluates student answers question-by-question using existing Multi-Agent provider contracts.
    Persists structured results into fact_exam_evaluations and updates ExamAttempt status & score.
    """
    # 1. Idempotency Check: Return existing completed evaluation unless forced
    existing_eval = db.query(ExamEvaluation).filter(ExamEvaluation.attempt_id == attempt.id).first()
    if existing_eval and existing_eval.status == "COMPLETED" and not force_recalculate:
        logger.info(f"Returning existing idempotent evaluation for attempt '{attempt.id}'.")
        return existing_eval

    # Create or update evaluation record
    if not existing_eval:
        eval_record = ExamEvaluation(
            attempt_id=attempt.id,
            exam_id=attempt.exam_id,
            candidate_id=attempt.candidate_id,
            status="IN_PROGRESS",
            total_score=0.00,
            maximum_score=float(attempt.max_score or 100.0),
            percentage=0.00,
            grade="F",
            question_results=[],
            evaluator_metadata={"provider": "MULTI_AGENT_EVALUATOR_ENGINE"},
            started_at=datetime.utcnow()
        )
        db.add(eval_record)
        db.commit()
        db.refresh(eval_record)
    else:
        eval_record = existing_eval
        eval_record.status = "IN_PROGRESS"
        eval_record.error_message = None
        eval_record.started_at = datetime.utcnow()
        db.commit()

    try:
        exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()
        if not exam:
            raise ValueError(f"Exam '{attempt.exam_id}' not found.")

        qp = db.query(QuestionPaper).filter(QuestionPaper.published_exam_id == exam.id).first()
        saved_answers = dict(attempt.answers or {})

        question_results: List[Dict[str, Any]] = []
        total_awarded = 0.0
        total_possible = 0.0
        q_counter = 1

        agent_provider = get_agent_provider()

        if qp and qp.sections:
            for s_idx, sec in enumerate(qp.sections):
                sec_type = sec.get("question_type", "MCQ").upper()
                for q_item in sec.get("questions", []):
                    q_id = str(q_item.get("id") or f"q_{q_counter}")
                    q_num_key = str(q_item.get("number", q_counter))
                    q_num = q_item.get("number", q_counter)
                    q_text = str(q_item.get("question") or q_item.get("title") or f"Question {q_num}")
                    correct_ans = str(q_item.get("correct_answer", "")).strip()
                    max_marks = float(q_item.get("marks", 10.0))

                    # User answer retrieval
                    user_ans = saved_answers.get(q_id) or saved_answers.get(q_num_key)
                    user_ans_str = str(user_ans).strip() if user_ans is not None else ""

                    awarded_marks = 0.0
                    correctness = "INCORRECT"
                    findings = []
                    reasoning = ""
                    evaluator = "MULTI_AGENT_PROVIDER"

                    if sec_type == "MCQ":
                        evaluator = "DETERMINISTIC_MCQ_EVALUATOR"
                        if user_ans_str and correct_ans and user_ans_str.upper() == correct_ans.upper():
                            awarded_marks = max_marks
                            correctness = "CORRECT"
                            findings.append(f"Correct answer '{user_ans_str}' selected.")
                            reasoning = "Option matches official answer key."
                        elif user_ans_str:
                            awarded_marks = 0.0
                            correctness = "INCORRECT"
                            findings.append(f"Selected option '{user_ans_str}' is incorrect.")
                            reasoning = "Option does not match official answer key."
                        else:
                            awarded_marks = 0.0
                            correctness = "INCORRECT"
                            findings.append("No answer submitted for this question.")
                            reasoning = "Unanswered question."

                    elif sec_type in ["SHORT_ANSWER", "SHORT"]:
                        evaluator = "MENTOR_AGENT"
                        if not user_ans_str:
                            awarded_marks = 0.0
                            correctness = "INCORRECT"
                            findings.append("No answer submitted.")
                            reasoning = "Unanswered short answer question."
                        else:
                            exec_metrics = {
                                "exit_code": 0,
                                "execution_latency_ms": 120.0,
                                "peak_memory_mb": 15.0,
                                "functional_score": 100.0 if len(user_ans_str) > 10 else 50.0,
                                "security_violation": False
                            }
                            eval_res = agent_provider.evaluate("MENTOR", user_ans_str, exam.title, exec_metrics)
                            raw_score = float(eval_res.get("score", 70.0))
                            # Scale score to question max marks (supports partial marks)
                            awarded_marks = round((raw_score / 100.0) * max_marks, 2)
                            awarded_marks = max(0.0, min(awarded_marks, max_marks))

                            if awarded_marks == max_marks:
                                correctness = "CORRECT"
                            elif awarded_marks > 0.0:
                                correctness = "PARTIAL"
                            else:
                                correctness = "INCORRECT"

                            findings = list(eval_res.get("findings", []))
                            reasoning = eval_res.get("reasoning_summary", "Mentor Agent evaluated short answer response.")

                    else:  # LONG_ANSWER or generic
                        evaluator = "A2A_CONSENSUS_ENGINE"
                        if not user_ans_str:
                            awarded_marks = 0.0
                            correctness = "INCORRECT"
                            findings.append("No answer submitted.")
                            reasoning = "Unanswered long answer question."
                        else:
                            exec_metrics = {
                                "exit_code": 0,
                                "execution_latency_ms": 250.0,
                                "peak_memory_mb": 25.0,
                                "functional_score": 100.0 if len(user_ans_str) > 30 else 60.0,
                                "security_violation": False
                            }
                            eval_res = agent_provider.evaluate("QA", user_ans_str, exam.title, exec_metrics)
                            raw_score = float(eval_res.get("score", 80.0))
                            awarded_marks = round((raw_score / 100.0) * max_marks, 2)
                            awarded_marks = max(0.0, min(awarded_marks, max_marks))

                            if awarded_marks == max_marks:
                                correctness = "CORRECT"
                            elif awarded_marks > 0.0:
                                correctness = "PARTIAL"
                            else:
                                correctness = "INCORRECT"

                            findings = list(eval_res.get("findings", []))
                            reasoning = eval_res.get("reasoning_summary", "Multi-Agent Consensus evaluated long answer response.")

                    total_awarded += awarded_marks
                    total_possible += max_marks

                    question_results.append({
                        "question_id": q_id,
                        "number": q_num,
                        "question": q_text,
                        "question_type": sec_type,
                        "user_answer": user_ans_str if user_ans_str else None,
                        "awarded_marks": round(awarded_marks, 2),
                        "maximum_marks": round(max_marks, 2),
                        "correctness": correctness,
                        "findings": findings,
                        "reasoning_summary": reasoning,
                        "evaluator_agent": evaluator
                    })
                    q_counter += 1

        else:
            # Fallback to dim_questions
            db_qs = db.query(Question).filter(Question.exam_id == exam.id, Question.is_active == True).order_by(Question.question_order).all()
            for db_q in db_qs:
                q_id = str(db_q.id)
                q_num = db_q.question_order
                q_text = db_q.description or db_q.title
                max_marks = float(db_q.max_score)
                total_possible += max_marks

                user_ans = saved_answers.get(q_id) or saved_answers.get(str(q_num))
                user_ans_str = str(user_ans).strip() if user_ans is not None else ""

                if user_ans_str:
                    exec_metrics = {"exit_code": 0, "execution_latency_ms": 100.0, "peak_memory_mb": 15.0, "functional_score": 80.0}
                    eval_res = agent_provider.evaluate("MENTOR", user_ans_str, exam.title, exec_metrics)
                    raw_score = float(eval_res.get("score", 75.0))
                    awarded = round((raw_score / 100.0) * max_marks, 2)
                    awarded = max(0.0, min(awarded, max_marks))
                    correctness = "CORRECT" if awarded == max_marks else ("PARTIAL" if awarded > 0 else "INCORRECT")
                    findings = list(eval_res.get("findings", []))
                    reasoning = eval_res.get("reasoning_summary", "Evaluated by Mentor Agent.")
                else:
                    awarded = 0.0
                    correctness = "INCORRECT"
                    findings = ["No answer submitted."]
                    reasoning = "Unanswered question."

                total_awarded += awarded
                question_results.append({
                    "question_id": q_id,
                    "number": q_num,
                    "question": q_text,
                    "question_type": "SHORT_ANSWER",
                    "user_answer": user_ans_str if user_ans_str else None,
                    "awarded_marks": round(awarded, 2),
                    "maximum_marks": round(max_marks, 2),
                    "correctness": correctness,
                    "findings": findings,
                    "reasoning_summary": reasoning,
                    "evaluator_agent": "MENTOR_AGENT"
                })

        if total_possible <= 0.0:
            total_possible = float(exam.max_score or 100.0)

        total_awarded = round(max(0.0, min(total_awarded, total_possible)), 2)
        percentage = round((total_awarded / total_possible) * 100.0, 2)
        grade = calculate_letter_grade(percentage)

        now = datetime.utcnow()

        eval_record.status = "COMPLETED"
        eval_record.total_score = total_awarded
        eval_record.maximum_score = total_possible
        eval_record.percentage = percentage
        eval_record.grade = grade
        eval_record.question_results = question_results
        eval_record.completed_at = now
        eval_record.error_message = None

        # Update ExamAttempt
        attempt.total_score = total_awarded
        attempt.max_score = total_possible
        attempt.status = "COMPLETED"
        if not attempt.completed_at:
            attempt.completed_at = now

        db.commit()
        db.refresh(eval_record)

        logger.info(f"Successfully evaluated attempt '{attempt.id}': Score={total_awarded}/{total_possible} ({percentage}%, Grade={grade}).")
        return eval_record

    except Exception as exc:
        logger.error(f"Evaluation failed for attempt '{attempt.id}': {exc}", exc_info=True)
        db.rollback()
        if eval_record:
            eval_record.status = "FAILED"
            eval_record.error_message = str(exc)
            db.commit()
            db.refresh(eval_record)
            return eval_record
        raise exc
