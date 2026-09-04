-- ============================================================================
-- PRODUCTION DDL SCHEMA: MULTI-AGENT EXAM & EVALUATION PORTAL STAR SCHEMA (PHASE 4)
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ----------------------------------------------------------------------------
-- DIMENSION 1: DIM_USERS (Candidates, Recruiters, Admins)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'candidate' CHECK (role IN ('candidate', 'recruiter', 'admin')),
    class_level INT CHECK (class_level IS NULL OR class_level BETWEEN 1 AND 12),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dim_users_email ON dim_users(email);
CREATE INDEX IF NOT EXISTS idx_dim_users_role ON dim_users(role);
CREATE INDEX IF NOT EXISTS idx_dim_users_class_level ON dim_users(class_level);

-- ----------------------------------------------------------------------------
-- DIMENSION 2: DIM_EXAMS (Exam catalog, publishing, attempt limits)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_exams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    difficulty VARCHAR(50) NOT NULL DEFAULT 'intermediate' CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')),
    duration_minutes INT NOT NULL DEFAULT 60 CHECK (duration_minutes > 0),
    max_score NUMERIC(5, 2) NOT NULL DEFAULT 100.00 CHECK (max_score > 0),
    max_attempts INT NOT NULL DEFAULT 1 CHECK (max_attempts > 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    created_by UUID REFERENCES dim_users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dim_exams_difficulty ON dim_exams(difficulty);
CREATE INDEX IF NOT EXISTS idx_dim_exams_active ON dim_exams(is_active);
CREATE INDEX IF NOT EXISTS idx_dim_exams_published ON dim_exams(is_published);

-- Insert Seed Baseline Exam if not present
INSERT INTO dim_exams (title, description, difficulty, duration_minutes, max_score, max_attempts, is_active, is_published)
VALUES (
    'Python Thread-Safe Queue & Optimization Assessment',
    'Implement a thread-safe Queue class with enqueue, dequeue, and capacity management.',
    'intermediate',
    60,
    100.00,
    3,
    TRUE,
    TRUE
) ON CONFLICT DO NOTHING;

-- ----------------------------------------------------------------------------
-- DIMENSION 3: DIM_SANDBOX_PROFILES (Resource limits & security profiles)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_sandbox_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    memory_limit_mb INT NOT NULL DEFAULT 128 CHECK (memory_limit_mb > 0),
    cpu_limit NUMERIC(3, 2) NOT NULL DEFAULT 0.50 CHECK (cpu_limit > 0),
    timeout_seconds INT NOT NULL DEFAULT 2 CHECK (timeout_seconds > 0),
    network_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    filesystem_read_only BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO dim_sandbox_profiles (name, memory_limit_mb, cpu_limit, timeout_seconds, network_enabled, filesystem_read_only)
VALUES ('default_python_sandbox', 128, 0.50, 2, FALSE, TRUE)
ON CONFLICT (name) DO NOTHING;

-- ----------------------------------------------------------------------------
-- DIMENSION 4: DIM_QUESTIONS (Question Bank)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_id UUID NOT NULL REFERENCES dim_exams(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    difficulty VARCHAR(50) NOT NULL DEFAULT 'intermediate' CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')),
    language VARCHAR(50) NOT NULL DEFAULT 'python',
    time_limit_seconds INT NOT NULL DEFAULT 2 CHECK (time_limit_seconds > 0),
    memory_limit_mb INT NOT NULL DEFAULT 128 CHECK (memory_limit_mb > 0),
    max_score NUMERIC(5, 2) NOT NULL DEFAULT 100.00 CHECK (max_score >= 0 AND max_score <= 100),
    question_order INT NOT NULL DEFAULT 1 CHECK (question_order > 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dim_questions_exam_id ON dim_questions(exam_id);
CREATE INDEX IF NOT EXISTS idx_dim_questions_difficulty ON dim_questions(difficulty);
CREATE INDEX IF NOT EXISTS idx_dim_questions_active ON dim_questions(is_active);
CREATE INDEX IF NOT EXISTS idx_dim_questions_exam_order ON dim_questions(exam_id, question_order);

-- ----------------------------------------------------------------------------
-- DIMENSION 5: DIM_TEST_CASES (Hidden & Visible Test Cases)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_test_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question_id UUID NOT NULL REFERENCES dim_questions(id) ON DELETE CASCADE,
    test_case_order INT NOT NULL DEFAULT 1 CHECK (test_case_order > 0),
    input_data TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    is_hidden BOOLEAN NOT NULL DEFAULT TRUE,
    weight NUMERIC(5, 2) NOT NULL DEFAULT 1.00 CHECK (weight > 0),
    timeout_seconds INT NOT NULL DEFAULT 2 CHECK (timeout_seconds > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dim_test_cases_question_id ON dim_test_cases(question_id);
CREATE INDEX IF NOT EXISTS idx_dim_test_cases_question_order ON dim_test_cases(question_id, test_case_order);

-- ----------------------------------------------------------------------------
-- FACT TABLE 1: FACT_EXAM_ATTEMPTS (Server-side Candidate Exam Attempts)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_exam_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES dim_users(id) ON DELETE CASCADE,
    exam_id UUID NOT NULL REFERENCES dim_exams(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'STARTED' CHECK (
        status IN ('STARTED', 'IN_PROGRESS', 'SUBMITTED', 'EVALUATING', 'COMPLETED', 'EXPIRED', 'CANCELLED')
    ),
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NOT NULL,
    submitted_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    total_score NUMERIC(5, 2) DEFAULT 0.00 CHECK (total_score >= 0 AND total_score <= 100),
    max_score NUMERIC(5, 2) DEFAULT 100.00 CHECK (max_score > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fact_attempts_candidate ON fact_exam_attempts(candidate_id);
CREATE INDEX IF NOT EXISTS idx_fact_attempts_exam ON fact_exam_attempts(exam_id);
CREATE INDEX IF NOT EXISTS idx_fact_attempts_status ON fact_exam_attempts(status);
CREATE INDEX IF NOT EXISTS idx_fact_attempts_started ON fact_exam_attempts(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_fact_attempts_expires ON fact_exam_attempts(expires_at);
CREATE INDEX IF NOT EXISTS idx_fact_attempts_cand_exam ON fact_exam_attempts(candidate_id, exam_id);

-- ----------------------------------------------------------------------------
-- FACT TABLE 2: FACT_SUBMISSIONS (Transactional Code Submissions)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_submissions (
    submission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES dim_users(id) ON DELETE CASCADE,
    exam_id UUID NOT NULL REFERENCES dim_exams(id) ON DELETE CASCADE,
    attempt_id UUID REFERENCES fact_exam_attempts(id) ON DELETE SET NULL,
    question_id UUID REFERENCES dim_questions(id) ON DELETE SET NULL,
    sandbox_profile_id UUID NOT NULL REFERENCES dim_sandbox_profiles(id) ON DELETE RESTRICT,
    
    -- Submission Core Payload
    language VARCHAR(50) NOT NULL DEFAULT 'python',
    source_code TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'QUEUED' CHECK (
        status IN (
            'QUEUED', 'STATIC_ANALYSIS', 'SANDBOX_RUNNING', 'TEST_CASE_EXECUTION', 
            'EXECUTION_COMPLETE', 'MCP_CONTEXT', 'ANOMALY_ANALYSIS', 'MENTOR_ANALYSIS', 
            'QA_ANALYSIS', 'A2A_CONSENSUS', 'ADAPTIVE_ANALYSIS', 'COMPLETED', 
            'FINALIZED', 'FAILED', 'TIMEOUT', 'SECURITY_BLOCKED'
        )
    ),
    celery_task_id VARCHAR(255),
    
    -- Security & AST Pre-screening
    static_analysis_status VARCHAR(50) DEFAULT 'PASSED',
    security_risk_level VARCHAR(50) DEFAULT 'LOW',
    
    -- Execution Virtualization & Functional Metrics
    functional_score NUMERIC(5, 2) DEFAULT 0.00 CHECK (functional_score >= 0 AND functional_score <= 100),
    execution_latency_ms DOUBLE PRECISION CHECK (execution_latency_ms IS NULL OR execution_latency_ms >= 0),
    peak_memory_mb DOUBLE PRECISION CHECK (peak_memory_mb IS NULL OR peak_memory_mb >= 0),
    exit_code INT,
    stdout TEXT,
    stderr TEXT,
    
    -- Proctoring & Behavioral Anomaly Metrics
    anomaly_score DOUBLE PRECISION DEFAULT 0.0 CHECK (anomaly_score IS NULL OR (anomaly_score >= 0.0 AND anomaly_score <= 1.0)),
    paste_ratio DOUBLE PRECISION DEFAULT 0.0,
    focus_loss_count INT DEFAULT 0 CHECK (focus_loss_count >= 0),
    typing_anomaly_score DOUBLE PRECISION DEFAULT 0.0 CHECK (typing_anomaly_score IS NULL OR (typing_anomaly_score >= 0.0 AND typing_anomaly_score <= 1.0)),
    
    -- MCP Context Injection
    mcp_context JSONB DEFAULT '{}'::jsonb,
    mcp_context_hash VARCHAR(64),
    
    -- Multi-Agent Evaluation & A2A Consensus
    mentor_score NUMERIC(5, 2) CHECK (mentor_score IS NULL OR (mentor_score >= 0 AND mentor_score <= 100)),
    qa_score NUMERIC(5, 2) CHECK (qa_score IS NULL OR (qa_score >= 0 AND qa_score <= 100)),
    consensus_score NUMERIC(5, 2) CHECK (consensus_score IS NULL OR (consensus_score >= 0 AND consensus_score <= 100)),
    consensus_confidence DOUBLE PRECISION DEFAULT 1.0 CHECK (consensus_confidence IS NULL OR (consensus_confidence >= 0.0 AND consensus_confidence <= 1.0)),
    a2a_consensus JSONB DEFAULT '{}'::jsonb,
    adaptive_challenge TEXT,
    evaluation_report TEXT,
    final_score NUMERIC(5, 2) CHECK (final_score IS NULL OR (final_score >= 0 AND final_score <= 100)),
    error_message TEXT,
    
    -- Timestamps
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fact_submissions_candidate_id ON fact_submissions(candidate_id);
CREATE INDEX IF NOT EXISTS idx_fact_submissions_exam_id ON fact_submissions(exam_id);
CREATE INDEX IF NOT EXISTS idx_fact_submissions_attempt_id ON fact_submissions(attempt_id);
CREATE INDEX IF NOT EXISTS idx_fact_submissions_question_id ON fact_submissions(question_id);
CREATE INDEX IF NOT EXISTS idx_fact_submissions_status ON fact_submissions(status);
CREATE INDEX IF NOT EXISTS idx_fact_submissions_created_at ON fact_submissions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_fact_submissions_completed_at ON fact_submissions(completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_fact_submissions_final_score ON fact_submissions(final_score);
CREATE INDEX IF NOT EXISTS idx_fact_submissions_anomaly_score ON fact_submissions(anomaly_score);
CREATE INDEX IF NOT EXISTS idx_fact_submissions_celery_task_id ON fact_submissions(celery_task_id);
CREATE INDEX IF NOT EXISTS idx_fact_submissions_cand_created ON fact_submissions(candidate_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_fact_submissions_exam_status ON fact_submissions(exam_id, status);

-- ----------------------------------------------------------------------------
-- FACT TABLE 3: FACT_TEST_RESULTS (Detailed Test Case Verification Results)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_test_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES fact_submissions(submission_id) ON DELETE CASCADE,
    test_case_id UUID NOT NULL REFERENCES dim_test_cases(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL CHECK (
        status IN ('PASSED', 'FAILED', 'TIMEOUT', 'RUNTIME_ERROR', 'SECURITY_BLOCKED', 'OUTPUT_LIMIT_EXCEEDED')
    ),
    execution_latency_ms DOUBLE PRECISION CHECK (execution_latency_ms IS NULL OR execution_latency_ms >= 0),
    peak_memory_mb DOUBLE PRECISION CHECK (peak_memory_mb IS NULL OR peak_memory_mb >= 0),
    exit_code INT,
    actual_output TEXT,
    expected_output_hash VARCHAR(64),
    error_message TEXT,
    score_awarded NUMERIC(5, 2) DEFAULT 0.00 CHECK (score_awarded >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fact_test_results_submission ON fact_test_results(submission_id);
CREATE INDEX IF NOT EXISTS idx_fact_test_results_test_case ON fact_test_results(test_case_id);
CREATE INDEX IF NOT EXISTS idx_fact_test_results_status ON fact_test_results(status);
