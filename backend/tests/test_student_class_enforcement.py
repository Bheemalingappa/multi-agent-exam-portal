import unittest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException
from pydantic import ValidationError

from app.api.auth import RegisterSchema, register_user, get_current_user_profile
from app.api.attempts import get_attempt_by_id, start_exam_attempt
from app.api.exams import assign_exam_endpoint, get_exam_by_id, list_exams, publish_exam
from app.api.exams import AssignExamRequest
from app.api.student_access import require_candidate_exam_access
from app.database.models import Exam, ExamAssignment, ExamAttempt, User
from app.schemas.exam import ExamCreateSchema
from app.api.exams import create_exam


class FakeQuery:
    def __init__(self, items):
        self.items = list(items)

    def filter(self, *args, **kwargs):
        for condition in args:
            key = getattr(getattr(condition, "left", None), "key", None)
            right = getattr(condition, "right", None)
            value = getattr(right, "value", None)
            operator_name = getattr(getattr(condition, "operator", None), "__name__", "")

            if key and operator_name == "eq":
                self.items = [item for item in self.items if getattr(item, key, None) == value]
            elif key == "id" and operator_name == "in_op":
                assignment_ids = {
                    getattr(item, "exam_id", None)
                    for item in getattr(right, "element", self).items
                } if hasattr(getattr(right, "element", None), "items") else {
                    getattr(item, "exam_id", None)
                    for item in getattr(right, "items", [])
                }
                if assignment_ids:
                    self.items = [item for item in self.items if getattr(item, "id", None) in assignment_ids]
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self.items[0] if self.items else None

    def all(self):
        return self.items

    def count(self):
        return len(self.items)

    def subquery(self):
        return self


class FakeDb:
    def __init__(self, *, users=None, exams=None, assignments=None, attempts=None):
        self.users = users or []
        self.exams = exams or []
        self.assignments = assignments or []
        self.attempts = attempts or []
        self.added = []

    def query(self, model):
        if model is User:
            return FakeQuery(self.users)
        if model is Exam:
            return FakeQuery(self.exams)
        if model is ExamAssignment:
            return FakeQuery(self.assignments)
        if model is ExamAttempt:
            return FakeQuery(self.attempts)
        return FakeQuery([])

    def add(self, item):
        self.added.append(item)
        if isinstance(item, User):
            self.users.append(item)
        if isinstance(item, Exam):
            self.exams.append(item)
        if isinstance(item, ExamAssignment):
            self.assignments.append(item)
        if isinstance(item, ExamAttempt):
            self.attempts.append(item)

    def commit(self):
        pass

    def refresh(self, item):
        if getattr(item, "id", None) is None:
            item.id = uuid.uuid4()
        if getattr(item, "created_at", None) is None:
            item.created_at = datetime.utcnow()


def make_user(role="candidate", class_level=None):
    return User(
        id=uuid.uuid4(),
        email=f"{uuid.uuid4()}@example.com",
        password_hash="hash",
        role=role,
        class_level=class_level,
        is_active=True,
        created_at=datetime.utcnow(),
    )


def make_exam(class_level=7, published=True):
    return Exam(
        id=uuid.uuid4(),
        title=f"Class {class_level} Exam",
        description="Assessment",
        class_level=class_level,
        subject="Kannada",
        language="Kannada",
        difficulty="intermediate",
        duration_minutes=60,
        max_score=Decimal("100.00"),
        max_attempts=1,
        is_active=True,
        is_published=published,
        created_at=datetime.utcnow(),
    )


def make_assignment(exam, class_level=7):
    return ExamAssignment(
        id=uuid.uuid4(),
        exam_id=exam.id,
        class_level=class_level,
        assigned_by=uuid.uuid4(),
        status="ACTIVE",
        created_at=datetime.utcnow(),
    )


def make_attempt(exam, student):
    return ExamAttempt(
        id=uuid.uuid4(),
        candidate_id=student.id,
        exam_id=exam.id,
        status="STARTED",
        started_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=60),
        total_score=Decimal("0.00"),
        max_score=Decimal("100.00"),
    )


class TestStudentClassEnforcement(unittest.TestCase):
    def test_candidate_registration_with_class_7(self):
        db = FakeDb()
        res = register_user(RegisterSchema(email="class7@example.com", password="secret123", role="candidate", class_level=7), db)
        self.assertEqual(res.class_level, 7)

    def test_candidate_registration_with_class_10(self):
        db = FakeDb()
        res = register_user(RegisterSchema(email="class10@example.com", password="secret123", role="candidate", class_level=10), db)
        self.assertEqual(res.class_level, 10)

    def test_invalid_class_0_rejected(self):
        with self.assertRaises(ValidationError):
            RegisterSchema(email="bad0@example.com", password="secret123", role="candidate", class_level=0)

    def test_invalid_class_13_rejected(self):
        with self.assertRaises(ValidationError):
            RegisterSchema(email="bad13@example.com", password="secret123", role="candidate", class_level=13)

    def test_auth_profile_returns_class_7(self):
        user = make_user(class_level=7)
        self.assertEqual(get_current_user_profile(user).class_level, 7)

    def test_auth_profile_returns_class_10(self):
        user = make_user(class_level=10)
        self.assertEqual(get_current_user_profile(user).class_level, 10)

    def test_published_unassigned_exam_denied(self):
        student = make_user(class_level=7)
        exam = make_exam(class_level=7, published=True)
        with self.assertRaises(HTTPException) as ctx:
            require_candidate_exam_access(FakeDb(exams=[exam]), exam, student)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_class_7_assignment_allows_class_7(self):
        student = make_user(class_level=7)
        exam = make_exam(class_level=7, published=True)
        require_candidate_exam_access(FakeDb(assignments=[make_assignment(exam, 7)]), exam, student)

    def test_class_7_assignment_denies_class_10(self):
        student = make_user(class_level=10)
        exam = make_exam(class_level=7, published=True)
        with self.assertRaises(HTTPException) as ctx:
            require_candidate_exam_access(FakeDb(assignments=[make_assignment(exam, 7)]), exam, student)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_class_10_cannot_directly_access_class_7_exam(self):
        student = make_user(class_level=10)
        exam = make_exam(class_level=7, published=True)
        db = FakeDb(exams=[exam], assignments=[make_assignment(exam, 7)])
        with self.assertRaises(HTTPException) as ctx:
            get_exam_by_id(str(exam.id), db, student)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_class_10_cannot_start_class_7_exam(self):
        student = make_user(class_level=10)
        exam = make_exam(class_level=7, published=True)
        db = FakeDb(exams=[exam], assignments=[make_assignment(exam, 7)])
        with self.assertRaises(HTTPException) as ctx:
            start_exam_attempt(str(exam.id), db, student)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_student_cannot_access_another_students_attempt(self):
        class7_a = make_user(class_level=7)
        class7_b = make_user(class_level=7)
        exam = make_exam(class_level=7, published=True)
        attempt = make_attempt(exam, class7_a)
        db = FakeDb(exams=[exam], assignments=[make_assignment(exam, 7)], attempts=[attempt])
        with self.assertRaises(HTTPException) as ctx:
            get_attempt_by_id(str(attempt.id), db, class7_b)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_teacher_can_create_publish_and_assign_exam(self):
        teacher = make_user(role="recruiter")
        db = FakeDb()
        exam = create_exam(
            ExamCreateSchema(
                title="Class 7 Kannada",
                description="Sandhi assessment",
                class_level=7,
                subject="Kannada",
                language="Kannada",
            ),
            db,
            teacher,
        )
        published = publish_exam(exam.id, db, teacher)
        assigned = assign_exam_endpoint(exam.id, AssignExamRequest(class_level=7), db, teacher)
        self.assertTrue(published.is_published)
        self.assertEqual(assigned["class_level"], 7)

    def test_candidate_listing_ignores_query_class_as_authority(self):
        student = make_user(class_level=10)
        exam = make_exam(class_level=7, published=True)
        db = FakeDb(exams=[exam], assignments=[make_assignment(exam, 7)])
        listed = list_exams(class_level=7, subject=None, language=None, db=db, current_user=student)
        self.assertEqual(listed, [])


if __name__ == "__main__":
    unittest.main()
