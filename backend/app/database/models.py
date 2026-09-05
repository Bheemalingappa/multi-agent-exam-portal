import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, Numeric
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database.session import Base

class Organization(Base):
    __tablename__ = "dim_organizations"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    max_candidates = Column(Integer, nullable=False, default=500)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

class User(Base):
    __tablename__ = "dim_users"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="candidate", index=True)
    class_level = Column(Integer, nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    submissions = relationship("SubmissionFact", back_populates="candidate", cascade="all, delete-orphan")
    attempts = relationship("ExamAttempt", back_populates="candidate", cascade="all, delete-orphan")
    created_exams = relationship("Exam", back_populates="creator")

class Exam(Base):
    __tablename__ = "dim_exams"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    class_level = Column(Integer, nullable=False, default=10, index=True)
    subject = Column(String(100), nullable=False, default="Mathematics", index=True)
    language = Column(String(50), nullable=False, default="English", index=True)
    difficulty = Column(String(50), nullable=False, default="intermediate", index=True)
    duration_minutes = Column(Integer, nullable=False, default=60)
    max_score = Column(Numeric(5, 2), nullable=False, default=100.00)
    max_attempts = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_published = Column(Boolean, nullable=False, default=False, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("dim_users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    creator = relationship("User", back_populates="created_exams")
    questions = relationship("Question", back_populates="exam", cascade="all, delete-orphan")
    attempts = relationship("ExamAttempt", back_populates="exam", cascade="all, delete-orphan")
    submissions = relationship("SubmissionFact", back_populates="exam", cascade="all, delete-orphan")
    assignments = relationship("ExamAssignment", back_populates="exam", cascade="all, delete-orphan")

class ExamAssignment(Base):
    __tablename__ = "fact_exam_assignments"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("dim_exams.id", ondelete="CASCADE"), nullable=False, index=True)
    class_level = Column(Integer, nullable=False, index=True)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("dim_users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), nullable=False, default="ACTIVE", index=True)
    start_at = Column(DateTime(timezone=True), nullable=True)
    end_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    exam = relationship("Exam", back_populates="assignments")
    assigner = relationship("User")

class SandboxProfile(Base):
    __tablename__ = "dim_sandbox_profiles"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    memory_limit_mb = Column(Integer, nullable=False, default=128)
    cpu_limit = Column(Numeric(3, 2), nullable=False, default=0.50)
    timeout_seconds = Column(Integer, nullable=False, default=2)
    network_enabled = Column(Boolean, nullable=False, default=False)
    filesystem_read_only = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    submissions = relationship("SandboxProfile", back_populates="sandbox_profile") if False else relationship("SubmissionFact", back_populates="sandbox_profile")


class Question(Base):
    __tablename__ = "dim_questions"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("dim_exams.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(50), nullable=False, default="intermediate", index=True)
    language = Column(String(50), nullable=False, default="python")
    time_limit_seconds = Column(Integer, nullable=False, default=2)
    memory_limit_mb = Column(Integer, nullable=False, default=128)
    max_score = Column(Numeric(5, 2), nullable=False, default=100.00)
    question_order = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    exam = relationship("Exam", back_populates="questions")
    test_cases = relationship("TestCase", back_populates="question", cascade="all, delete-orphan")
    submissions = relationship("SubmissionFact", back_populates="question")

class TestCase(Base):
    __tablename__ = "dim_test_cases"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("dim_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    test_case_order = Column(Integer, nullable=False, default=1)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_hidden = Column(Boolean, nullable=False, default=True)
    weight = Column(Numeric(5, 2), nullable=False, default=1.00)
    timeout_seconds = Column(Integer, nullable=False, default=2)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    question = relationship("Question", back_populates="test_cases")
    test_results = relationship("TestResult", back_populates="test_case", cascade="all, delete-orphan")

class ExamAttempt(Base):
    __tablename__ = "fact_exam_attempts"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("dim_users.id", ondelete="CASCADE"), nullable=False, index=True)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("dim_exams.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="STARTED", index=True)
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    answers = Column(JSONB, nullable=False, default=dict)
    total_score = Column(Numeric(5, 2), default=0.00)
    max_score = Column(Numeric(5, 2), default=100.00)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    candidate = relationship("User", back_populates="attempts")
    exam = relationship("Exam", back_populates="attempts")
    submissions = relationship("SubmissionFact", back_populates="attempt")

class SubmissionFact(Base):
    __tablename__ = "fact_submissions"
    __table_args__ = {'extend_existing': True}

    submission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("dim_users.id", ondelete="CASCADE"), nullable=False, index=True)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("dim_exams.id", ondelete="CASCADE"), nullable=False, index=True)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("fact_exam_attempts.id", ondelete="SET NULL"), nullable=True, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("dim_questions.id", ondelete="SET NULL"), nullable=True, index=True)
    sandbox_profile_id = Column(UUID(as_uuid=True), ForeignKey("dim_sandbox_profiles.id", ondelete="RESTRICT"), nullable=False)

    language = Column(String(50), nullable=False, default="python")
    source_code = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="QUEUED", index=True)
    celery_task_id = Column(String(255), nullable=True, index=True)

    static_analysis_status = Column(String(50), default="PASSED")
    security_risk_level = Column(String(50), default="LOW")

    functional_score = Column(Numeric(5, 2), default=0.00)
    execution_latency_ms = Column(Float, nullable=True)
    peak_memory_mb = Column(Float, nullable=True)
    exit_code = Column(Integer, nullable=True)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)

    anomaly_score = Column(Float, default=0.0, index=True)
    paste_ratio = Column(Float, default=0.0)
    focus_loss_count = Column(Integer, default=0)
    typing_anomaly_score = Column(Float, default=0.0)

    mcp_context = Column(JSONB, default=dict)
    mcp_context_hash = Column(String(64), nullable=True)

    mentor_score = Column(Numeric(5, 2), nullable=True)
    qa_score = Column(Numeric(5, 2), nullable=True)
    consensus_score = Column(Numeric(5, 2), nullable=True)
    consensus_confidence = Column(Float, default=1.0)
    a2a_consensus = Column(JSONB, default=dict)
    adaptive_challenge = Column(Text, nullable=True)
    evaluation_report = Column(Text, nullable=True)
    final_score = Column(Numeric(5, 2), nullable=True, index=True)
    error_message = Column(Text, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    candidate = relationship("User", back_populates="submissions")
    exam = relationship("Exam", back_populates="submissions")
    sandbox_profile = relationship("SandboxProfile", back_populates="submissions")
    attempt = relationship("ExamAttempt", back_populates="submissions")
    question = relationship("Question", back_populates="submissions")
    test_results = relationship("TestResult", back_populates="submission", cascade="all, delete-orphan")
    agent_evaluations = relationship("AgentEvaluation", back_populates="submission", cascade="all, delete-orphan")
    agent_consensus = relationship("AgentConsensus", back_populates="submission", cascade="all, delete-orphan")

class TestResult(Base):
    __tablename__ = "fact_test_results"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("fact_submissions.submission_id", ondelete="CASCADE"), nullable=False, index=True)
    test_case_id = Column(UUID(as_uuid=True), ForeignKey("dim_test_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)
    execution_latency_ms = Column(Float, nullable=True)
    peak_memory_mb = Column(Float, nullable=True)
    exit_code = Column(Integer, nullable=True)
    actual_output = Column(Text, nullable=True)
    expected_output_hash = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)
    score_awarded = Column(Numeric(5, 2), default=0.00)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    submission = relationship("SubmissionFact", back_populates="test_results")
    test_case = relationship("TestCase", back_populates="test_results")

class AgentEvaluation(Base):
    __tablename__ = "fact_agent_evaluations"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("fact_submissions.submission_id", ondelete="CASCADE"), nullable=False, index=True)
    agent_type = Column(String(50), nullable=False, index=True)
    round_number = Column(Integer, nullable=False, default=1)
    score = Column(Numeric(5, 2), nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)
    risk_level = Column(String(50), default="LOW")
    findings = Column(JSONB, default=list)
    reasoning_summary = Column(Text, nullable=True)
    latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    submission = relationship("SubmissionFact", back_populates="agent_evaluations")

class AgentConsensus(Base):
    __tablename__ = "fact_agent_consensus"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("fact_submissions.submission_id", ondelete="CASCADE"), nullable=False, index=True)
    round_count = Column(Integer, nullable=False, default=1)
    mentor_score = Column(Numeric(5, 2), nullable=True)
    qa_score = Column(Numeric(5, 2), nullable=True)
    security_score = Column(Numeric(5, 2), nullable=True)
    consensus_score = Column(Numeric(5, 2), nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)
    consensus_method = Column(String(100), default="WEIGHTED_MULTI_AGENT_CONSENSUS")
    disagreement_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    submission = relationship("SubmissionFact", back_populates="agent_consensus")

class AIUsageFact(Base):
    __tablename__ = "fact_ai_usage"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("fact_submissions.submission_id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False)
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    latency_ms = Column(Float, default=0.0)
    estimated_cost = Column(Numeric(10, 6), default=0.0)
    status = Column(String(50), default="SUCCESS")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

class PlagiarismResultFact(Base):
    __tablename__ = "fact_plagiarism_results"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("fact_submissions.submission_id", ondelete="CASCADE"), nullable=False, index=True)
    compared_submission_id = Column(UUID(as_uuid=True), ForeignKey("fact_submissions.submission_id", ondelete="CASCADE"), nullable=True)
    ast_similarity_score = Column(Numeric(5, 2), default=0.00)
    token_similarity_score = Column(Numeric(5, 2), default=0.00)
    semantic_similarity_score = Column(Numeric(5, 2), default=0.00)
    plagiarism_risk_level = Column(String(20), default="LOW")
    matching_evidence = Column(JSONB, default=list)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

class HumanReviewFact(Base):
    __tablename__ = "fact_human_reviews"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("fact_submissions.submission_id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("dim_users.id", ondelete="CASCADE"), nullable=False)
    original_score = Column(Numeric(5, 2), nullable=False)
    override_score = Column(Numeric(5, 2), nullable=False)
    review_status = Column(String(50), default="APPROVED")
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

class AuditEventFact(Base):
    __tablename__ = "fact_audit_events"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("dim_users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=False)
    event_metadata = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

class QuestionPaper(Base):
    __tablename__ = "dim_question_papers"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    class_level = Column(Integer, nullable=False, default=10, index=True)
    subject = Column(String(100), nullable=False, index=True)
    language = Column(String(50), nullable=False, default="English", index=True)
    topic = Column(String(255), nullable=False)
    difficulty = Column(String(50), nullable=False, default="medium")
    duration_minutes = Column(Integer, nullable=False, default=60)
    maximum_marks = Column(Numeric(5, 2), nullable=False, default=100.00)
    generation_provider = Column(String(50), nullable=False, default="DETERMINISTIC_FALLBACK")
    source_type = Column(String(50), nullable=True, default="TOPIC_ONLY")
    source_document_id = Column(String(255), nullable=True)
    source_context = Column(Text, nullable=True)
    exact_topic = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="DRAFT", index=True)
    instructions = Column(Text, nullable=False, default="1. Answer all questions.\n2. Show mathematical steps where required.\n3. Read each question carefully.")
    sections = Column(JSONB, nullable=False, default=list)
    published_exam_id = Column(UUID(as_uuid=True), ForeignKey("dim_exams.id", ondelete="SET NULL"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("dim_users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    creator = relationship("User")
    published_exam = relationship("Exam")

class ExamEvaluation(Base):
    __tablename__ = "fact_exam_evaluations"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("fact_exam_attempts.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("dim_exams.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("dim_users.id", ondelete="CASCADE"), nullable=False, index=True)

    status = Column(String(50), nullable=False, default="COMPLETED", index=True)
    total_score = Column(Numeric(5, 2), nullable=False, default=0.00)
    maximum_score = Column(Numeric(5, 2), nullable=False, default=100.00)
    percentage = Column(Numeric(5, 2), nullable=False, default=0.00)
    grade = Column(String(10), nullable=False, default="F")

    question_results = Column(JSONB, nullable=False, default=list)
    evaluator_metadata = Column(JSONB, nullable=False, default=dict)
    error_message = Column(Text, nullable=True)

    started_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    attempt = relationship("ExamAttempt", backref="evaluation")
    exam = relationship("Exam")
    candidate = relationship("User")

