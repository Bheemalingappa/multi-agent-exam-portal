-- ============================================================================
-- PHASE 5 MIGRATION: AGENT EVALUATIONS & CONSENSUS FACT TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS fact_agent_evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES fact_submissions(submission_id) ON DELETE CASCADE,
    agent_type VARCHAR(50) NOT NULL CHECK (agent_type IN ('MENTOR', 'QA', 'SECURITY', 'CONSENSUS', 'ADAPTIVE')),
    round_number INT NOT NULL DEFAULT 1 CHECK (round_number > 0),
    score NUMERIC(5, 2) NOT NULL CHECK (score >= 0 AND score <= 100),
    confidence DOUBLE PRECISION NOT NULL DEFAULT 1.0 CHECK (confidence >= 0.0 AND confidence <= 1.0),
    risk_level VARCHAR(50) DEFAULT 'LOW',
    findings JSONB DEFAULT '[]'::jsonb,
    reasoning_summary TEXT,
    latency_ms DOUBLE PRECISION DEFAULT 0.0 CHECK (latency_ms >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fact_agent_eval_submission ON fact_agent_evaluations(submission_id);
CREATE INDEX IF NOT EXISTS idx_fact_agent_eval_type ON fact_agent_evaluations(agent_type);
CREATE INDEX IF NOT EXISTS idx_fact_agent_eval_sub_type ON fact_agent_evaluations(submission_id, agent_type);

CREATE TABLE IF NOT EXISTS fact_agent_consensus (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES fact_submissions(submission_id) ON DELETE CASCADE,
    round_count INT NOT NULL DEFAULT 1 CHECK (round_count > 0),
    mentor_score NUMERIC(5, 2) CHECK (mentor_score >= 0 AND mentor_score <= 100),
    qa_score NUMERIC(5, 2) CHECK (qa_score >= 0 AND qa_score <= 100),
    security_score NUMERIC(5, 2) CHECK (security_score >= 0 AND security_score <= 100),
    consensus_score NUMERIC(5, 2) NOT NULL CHECK (consensus_score >= 0 AND consensus_score <= 100),
    confidence DOUBLE PRECISION NOT NULL DEFAULT 1.0 CHECK (confidence >= 0.0 AND confidence <= 1.0),
    consensus_method VARCHAR(100) NOT NULL DEFAULT 'WEIGHTED_MULTI_AGENT_CONSENSUS',
    disagreement_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fact_agent_consensus_sub ON fact_agent_consensus(submission_id);
