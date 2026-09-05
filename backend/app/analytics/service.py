import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case, desc, or_
from app.database.models import (
    ExamAttempt, ExamEvaluation, Exam, QuestionPaper,
    ExamAssignment, User
)
from app.services.evaluation_service import calculate_letter_grade

logger = logging.getLogger(__name__)

class AnalyticsService:
    """
    High-performance Analytics Engine computing student results, performance trends,
    teacher summary metrics, exam-level performance, question-wise accuracy,
    topic performance, and student rosters with strict authorization scoping.
    """

    @staticmethod
    def get_student_summary(db: Session, candidate_id: str) -> Dict[str, Any]:
        """
        Student Results Summary: Total attempted, completed, average %, latest result,
        highest score, current grade, and recent exam results list.
        """
        attempts = db.query(ExamAttempt).filter(ExamAttempt.candidate_id == candidate_id).all()
        total_attempted = len(attempts)

        evaluations = (
            db.query(ExamEvaluation, Exam.title, Exam.subject)
            .join(Exam, ExamEvaluation.exam_id == Exam.id)
            .filter(ExamEvaluation.candidate_id == candidate_id, ExamEvaluation.status == "COMPLETED")
            .order_by(desc(ExamEvaluation.completed_at), desc(ExamEvaluation.created_at))
            .all()
        )

        completed_count = len(evaluations)

        if completed_count == 0:
            return {
                "total_attempted": total_attempted,
                "completed_exams": 0,
                "average_percentage": 0.0,
                "highest_score": 0.0,
                "current_grade": "N/A",
                "latest_result": None,
                "recent_results": []
            }

        percentages = [float(ev[0].percentage or 0.0) for ev in evaluations]
        avg_percentage = round(sum(percentages) / completed_count, 2)
        highest_score = round(max(percentages), 2)
        current_grade = calculate_letter_grade(avg_percentage)

        latest_ev, latest_title, latest_subject = evaluations[0]
        latest_result = {
            "evaluation_id": str(latest_ev.id),
            "attempt_id": str(latest_ev.attempt_id),
            "exam_id": str(latest_ev.exam_id),
            "exam_title": latest_title,
            "subject": latest_subject,
            "score": float(latest_ev.total_score or 0.0),
            "max_score": float(latest_ev.maximum_score or 100.0),
            "percentage": float(latest_ev.percentage or 0.0),
            "grade": latest_ev.grade,
            "completed_at": latest_ev.completed_at.isoformat() if latest_ev.completed_at else latest_ev.created_at.isoformat()
        }

        recent_results = []
        for ev, e_title, e_subject in evaluations[:10]:
            recent_results.append({
                "evaluation_id": str(ev.id),
                "attempt_id": str(ev.attempt_id),
                "exam_id": str(ev.exam_id),
                "exam_title": e_title,
                "subject": e_subject,
                "score": float(ev.total_score or 0.0),
                "max_score": float(ev.maximum_score or 100.0),
                "percentage": float(ev.percentage or 0.0),
                "grade": ev.grade,
                "date": (ev.completed_at or ev.created_at).strftime("%Y-%m-%d"),
                "status": "COMPLETED"
            })

        return {
            "total_attempted": total_attempted,
            "completed_exams": completed_count,
            "average_percentage": avg_percentage,
            "highest_score": highest_score,
            "current_grade": current_grade,
            "latest_result": latest_result,
            "recent_results": recent_results
        }

    @staticmethod
    def get_student_performance(db: Session, candidate_id: str) -> Dict[str, Any]:
        """
        Student Performance Analytics: Score trend timeline, subject-wise performance,
        grade distribution, and average percentage.
        """
        evaluations = (
            db.query(ExamEvaluation, Exam.title, Exam.subject)
            .join(Exam, ExamEvaluation.exam_id == Exam.id)
            .filter(ExamEvaluation.candidate_id == candidate_id, ExamEvaluation.status == "COMPLETED")
            .order_by(ExamEvaluation.completed_at.asc(), ExamEvaluation.created_at.asc())
            .all()
        )

        grade_counts = {"A+": 0, "A": 0, "B+": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        score_trend = []
        subject_map: Dict[str, List[float]] = {}

        for ev, e_title, e_subject in evaluations:
            pct = float(ev.percentage or 0.0)
            score_trend.append({
                "date": (ev.completed_at or ev.created_at).strftime("%Y-%m-%d"),
                "exam_title": e_title,
                "subject": e_subject,
                "score": float(ev.total_score or 0.0),
                "percentage": pct,
                "grade": ev.grade
            })

            g = (ev.grade or "F").upper()
            if g in grade_counts:
                grade_counts[g] += 1
            else:
                grade_counts["F"] += 1

            subj = e_subject or "General"
            if subj not in subject_map:
                subject_map[subj] = []
            subject_map[subj].append(pct)

        subject_performance = []
        for subj, pcts in subject_map.items():
            s_avg = round(sum(pcts) / len(pcts), 2)
            s_max = round(max(pcts), 2)
            subject_performance.append({
                "subject": subj,
                "total_exams": len(pcts),
                "average_percentage": s_avg,
                "highest_score": s_max,
                "grade": calculate_letter_grade(s_avg)
            })

        avg_percentage = round(sum(p["percentage"] for p in score_trend) / len(score_trend), 2) if score_trend else 0.0

        return {
            "average_percentage": avg_percentage,
            "score_trend": score_trend,
            "subject_performance": subject_performance,
            "grade_distribution": grade_counts
        }

    @staticmethod
    def _get_teacher_exam_ids(db: Session, teacher_id: str) -> List[str]:
        """
        Helper: Return list of exam IDs owned or assigned by the authenticated teacher.
        """
        qp_exam_ids = [
            str(e_id) for (e_id,) in db.query(QuestionPaper.published_exam_id)
            .filter(QuestionPaper.created_by == teacher_id, QuestionPaper.published_exam_id.isnot(None))
            .all()
        ]
        assign_exam_ids = [
            str(e_id) for (e_id,) in db.query(ExamAssignment.exam_id)
            .filter(ExamAssignment.assigned_by == teacher_id)
            .all()
        ]
        exam_ids = [
            str(e_id) for (e_id,) in db.query(Exam.id)
            .filter(Exam.created_by == teacher_id)
            .all()
        ]

        combined = list(set(qp_exam_ids + assign_exam_ids + exam_ids))
        return combined

    @staticmethod
    def get_teacher_summary(db: Session, teacher_id: str) -> Dict[str, Any]:
        """
        Teacher Analytics Summary: Total papers, published exams, active assignments,
        total submissions, average/highest/lowest score, and pass percentage for teacher's exams.
        """
        total_qps = db.query(QuestionPaper).filter(QuestionPaper.created_by == teacher_id).count()
        published_exams = db.query(QuestionPaper).filter(
            QuestionPaper.created_by == teacher_id,
            QuestionPaper.status.in_(["PUBLISHED", "ASSIGNED"])
        ).count()

        active_assignments = db.query(ExamAssignment).filter(
            ExamAssignment.assigned_by == teacher_id,
            ExamAssignment.is_active == True
        ).count()

        teacher_exam_ids = AnalyticsService._get_teacher_exam_ids(db, teacher_id)

        if not teacher_exam_ids:
            return {
                "total_question_papers": total_qps,
                "published_exams": published_exams,
                "active_assignments": active_assignments,
                "total_submissions": 0,
                "average_score": 0.0,
                "highest_score": 0.0,
                "lowest_score": 0.0,
                "pass_percentage": 0.0
            }

        evaluations = db.query(ExamEvaluation).filter(
            ExamEvaluation.exam_id.in_(teacher_exam_ids),
            ExamEvaluation.status == "COMPLETED"
        ).all()

        total_subs = len(evaluations)
        if total_subs == 0:
            return {
                "total_question_papers": total_qps,
                "published_exams": published_exams,
                "active_assignments": active_assignments,
                "total_submissions": 0,
                "average_score": 0.0,
                "highest_score": 0.0,
                "lowest_score": 0.0,
                "pass_percentage": 0.0
            }

        pcts = [float(ev.percentage or 0.0) for ev in evaluations]
        avg_score = round(sum(pcts) / total_subs, 2)
        highest_score = round(max(pcts), 2)
        lowest_score = round(min(pcts), 2)

        passed_count = sum(1 for p in pcts if p >= 40.0)
        pass_percentage = round((passed_count / total_subs) * 100.0, 2)

        return {
            "total_question_papers": total_qps,
            "published_exams": published_exams,
            "active_assignments": active_assignments,
            "total_submissions": total_subs,
            "average_score": avg_score,
            "highest_score": highest_score,
            "lowest_score": lowest_score,
            "pass_percentage": pass_percentage
        }

    @staticmethod
    def get_exam_performance(db: Session, exam_id: str, teacher_id: str) -> Dict[str, Any]:
        """
        Exam Performance View: Assigned students count, submission count, submission %,
        avg/highest/lowest score, pass rate, grade distribution, and exact_topic analytics.
        """
        teacher_exam_ids = AnalyticsService._get_teacher_exam_ids(db, teacher_id)
        if str(exam_id) not in teacher_exam_ids:
            raise PermissionError(f"Teacher '{teacher_id}' is not authorized to access exam '{exam_id}' analytics.")

        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            raise ValueError(f"Exam '{exam_id}' not found.")

        qp = db.query(QuestionPaper).filter(QuestionPaper.published_exam_id == exam.id).first()

        assignments = db.query(ExamAssignment).filter(ExamAssignment.exam_id == exam.id, ExamAssignment.is_active == True).all()
        assigned_classes = [a.class_level for a in assignments if a.class_level is not None]
        if assigned_classes:
            assigned_students_count = db.query(User).filter(User.role == "candidate", User.class_level.in_(assigned_classes)).count()
        else:
            assigned_students_count = db.query(User).filter(User.role == "candidate", User.class_level == exam.class_level).count()

        if assigned_students_count == 0:
            assigned_students_count = max(1, db.query(ExamAttempt).filter(ExamAttempt.exam_id == exam.id).count())

        evaluations = db.query(ExamEvaluation).filter(
            ExamEvaluation.exam_id == exam.id,
            ExamEvaluation.status == "COMPLETED"
        ).all()

        total_submissions = len(evaluations)
        submission_pct = round((total_submissions / assigned_students_count) * 100.0, 2) if assigned_students_count > 0 else 0.0

        grade_counts = {"A+": 0, "A": 0, "B+": 0, "B": 0, "C": 0, "D": 0, "F": 0}

        if total_submissions == 0:
            avg_score = 0.0
            highest_score = 0.0
            lowest_score = 0.0
            pass_rate = 0.0
        else:
            pcts = [float(ev.percentage or 0.0) for ev in evaluations]
            avg_score = round(sum(pcts) / total_submissions, 2)
            highest_score = round(max(pcts), 2)
            lowest_score = round(min(pcts), 2)
            passed = sum(1 for p in pcts if p >= 40.0)
            pass_rate = round((passed / total_submissions) * 100.0, 2)

            for ev in evaluations:
                g = (ev.grade or "F").upper()
                if g in grade_counts:
                    grade_counts[g] += 1
                else:
                    grade_counts["F"] += 1

        topic_name = (qp.exact_topic if qp and qp.exact_topic else (qp.topic if qp else exam.title))
        topic_performance = [{
            "topic": topic_name,
            "source_mode": qp.source_type if qp else "TOPIC_ONLY",
            "attempts_count": total_submissions,
            "average_score": avg_score,
            "mastery_percentage": avg_score
        }]

        return {
            "exam_id": str(exam.id),
            "exam_title": exam.title,
            "subject": exam.subject,
            "class_level": exam.class_level,
            "assigned_students": assigned_students_count,
            "total_submissions": total_submissions,
            "submission_percentage": submission_pct,
            "average_score": avg_score,
            "highest_score": highest_score,
            "lowest_score": lowest_score,
            "pass_rate": pass_rate,
            "grade_distribution": grade_counts,
            "topic_performance": topic_performance
        }

    @staticmethod
    def get_exam_questions_analytics(db: Session, exam_id: str, teacher_id: str) -> Dict[str, Any]:
        """
        Question-Wise Analytics: Number of attempts, correct count, incorrect count,
        skipped count, accuracy %, average marks awarded, maximum marks, and difficulty flags.
        """
        teacher_exam_ids = AnalyticsService._get_teacher_exam_ids(db, teacher_id)
        if str(exam_id) not in teacher_exam_ids:
            raise PermissionError(f"Teacher '{teacher_id}' is not authorized to access question analytics for exam '{exam_id}'.")

        evaluations = db.query(ExamEvaluation).filter(
            ExamEvaluation.exam_id == exam_id,
            ExamEvaluation.status == "COMPLETED"
        ).all()

        qp = db.query(QuestionPaper).filter(QuestionPaper.published_exam_id == exam_id).first()

        q_stats: Dict[str, Dict[str, Any]] = {}

        if qp and qp.sections:
            q_num = 1
            for sec in qp.sections:
                sec_type = sec.get("question_type", "MCQ")
                for q_item in sec.get("questions", []):
                    q_id = str(q_item.get("id") or f"q_{q_num}")
                    q_stats[q_id] = {
                        "question_id": q_id,
                        "number": q_item.get("number", q_num),
                        "question": q_item.get("question") or q_item.get("title") or f"Question {q_num}",
                        "question_type": sec_type,
                        "maximum_marks": float(q_item.get("marks", 10.0)),
                        "attempts_count": 0,
                        "correct_count": 0,
                        "incorrect_count": 0,
                        "skipped_count": 0,
                        "total_awarded": 0.0
                    }
                    q_num += 1

        for ev in evaluations:
            q_results = ev.question_results or []
            for qr in q_results:
                q_id = str(qr.get("question_id") or f"q_{qr.get('number', 1)}")
                if q_id not in q_stats:
                    q_stats[q_id] = {
                        "question_id": q_id,
                        "number": qr.get("number", 1),
                        "question": qr.get("question", f"Question {qr.get('number', 1)}"),
                        "question_type": qr.get("question_type", "MCQ"),
                        "maximum_marks": float(qr.get("maximum_marks", 10.0)),
                        "attempts_count": 0,
                        "correct_count": 0,
                        "incorrect_count": 0,
                        "skipped_count": 0,
                        "total_awarded": 0.0
                    }

                st = q_stats[q_id]
                st["attempts_count"] += 1
                st["total_awarded"] += float(qr.get("awarded_marks", 0.0))

                ans = qr.get("user_answer")
                if ans is None or str(ans).strip() == "":
                    st["skipped_count"] += 1

                c_status = str(qr.get("correctness", "INCORRECT")).upper()
                if c_status == "CORRECT":
                    st["correct_count"] += 1
                elif c_status == "PARTIAL":
                    st["incorrect_count"] += 1
                else:
                    st["incorrect_count"] += 1

        questions_list = []
        for q_id, st in q_stats.items():
            att = st["attempts_count"]
            acc = round((st["correct_count"] / att) * 100.0, 2) if att > 0 else 0.0
            avg_marks = round(st["total_awarded"] / att, 2) if att > 0 else 0.0
            is_difficult = (acc < 50.0 and att > 0)

            questions_list.append({
                "question_id": q_id,
                "number": st["number"],
                "question": st["question"],
                "question_type": st["question_type"],
                "maximum_marks": st["maximum_marks"],
                "attempts_count": att,
                "correct_count": st["correct_count"],
                "incorrect_count": st["incorrect_count"],
                "skipped_count": st["skipped_count"],
                "accuracy_percentage": acc,
                "average_marks_awarded": avg_marks,
                "is_difficult": is_difficult
            })

        questions_list.sort(key=lambda x: x["number"])

        return {
            "exam_id": str(exam_id),
            "total_questions": len(questions_list),
            "questions": questions_list
        }

    @staticmethod
    def get_exam_students_roster(db: Session, exam_id: str, teacher_id: str) -> Dict[str, Any]:
        """
        Student Performance Table for Teacher: Roster of all student attempts and evaluations,
        with sorting support and performance flags.
        """
        teacher_exam_ids = AnalyticsService._get_teacher_exam_ids(db, teacher_id)
        if str(exam_id) not in teacher_exam_ids:
            raise PermissionError(f"Teacher '{teacher_id}' is not authorized to access student roster for exam '{exam_id}'.")

        attempts = (
            db.query(ExamAttempt, User)
            .join(User, ExamAttempt.candidate_id == User.id)
            .filter(ExamAttempt.exam_id == exam_id)
            .order_by(ExamAttempt.created_at.desc())
            .all()
        )

        evaluations_by_attempt = {
            str(ev.attempt_id): ev for ev in db.query(ExamEvaluation).filter(ExamEvaluation.exam_id == exam_id).all()
        }

        students_roster = []
        for att, user in attempts:
            att_id = str(att.id)
            ev = evaluations_by_attempt.get(att_id)

            if ev and ev.status == "COMPLETED":
                score = float(ev.total_score or 0.0)
                max_score = float(ev.maximum_score or 100.0)
                pct = float(ev.percentage or 0.0)
                grade = ev.grade
                eval_status = "COMPLETED"
            elif att.status in ["SUBMITTED", "COMPLETED"]:
                score = float(att.total_score or 0.0)
                max_score = float(att.max_score or 100.0)
                pct = round((score / max_score) * 100.0, 2) if max_score > 0 else 0.0
                grade = calculate_letter_grade(pct)
                eval_status = "IN_PROGRESS"
            else:
                score = 0.0
                max_score = float(att.max_score or 100.0)
                pct = 0.0
                grade = "F"
                eval_status = att.status

            if pct >= 85.0:
                flag = "High Performer"
            elif pct >= 60.0:
                flag = "Average"
            elif eval_status in ["COMPLETED", "SUBMITTED"]:
                flag = "Needs Improvement"
            else:
                flag = "Not Submitted"

            students_roster.append({
                "attempt_id": att_id,
                "candidate_id": str(user.id),
                "email": user.email,
                "class_level": user.class_level or 10,
                "score": score,
                "max_score": max_score,
                "percentage": pct,
                "grade": grade,
                "submitted_at": att.submitted_at.isoformat() if att.submitted_at else (att.completed_at.isoformat() if att.completed_at else None),
                "evaluation_status": eval_status,
                "performance_flag": flag
            })

        return {
            "exam_id": str(exam_id),
            "total_students": len(students_roster),
            "students": students_roster
        }
