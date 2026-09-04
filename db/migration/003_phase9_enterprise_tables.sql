-- ============================================================================
-- PHASE 9 MIGRATION: ENTERPRISE TENANCY, AI USAGE, PLAGIARISM & AUDIT TRAIL
-- ============================================================================

CREATE TABLE IF NOT EXISTS dim_organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    max_candidates INT NOT NULL DEFAULT 500,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fact_ai_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES fact_submissions(submission_id) ON DELETE CASCADE,
    agent_name VARCHAR(50) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    input_tokens INT NOT NULL DEFAULT 0,
    output_tokens INT NOT NULL DEFAULT 0,
    total_tokens INT NOT NULL DEFAULT 0,
    latency_ms DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    estimated_cost NUMERIC(10, 6) NOT NULL DEFAULT 0.0,
    status VARCHAR(50) NOT NULL DEFAULT 'SUCCESS',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fact_plagiarism_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES fact_submissions(submission_id) ON DELETE CASCADE,
    compared_submission_id UUID REFERENCES fact_submissions(submission_id) ON DELETE CASCADE,
    ast_similarity_score NUMERIC(5, 2) NOT NULL DEFAULT 0.0,
    token_similarity_score NUMERIC(5, 2) NOT NULL DEFAULT 0.0,
    semantic_similarity_score NUMERIC(5, 2) NOT NULL DEFAULT 0.0,
    plagiarism_risk_level VARCHAR(20) NOT NULL DEFAULT 'LOW',
    matching_evidence JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fact_human_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES fact_submissions(submission_id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES dim_users(id) ON DELETE CASCADE,
    original_score NUMERIC(5, 2) NOT NULL,
    override_score NUMERIC(5, 2) NOT NULL,
    review_status VARCHAR(50) NOT NULL DEFAULT 'APPROVED',
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fact_audit_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_id UUID REFERENCES dim_users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_usage_submission ON fact_ai_usage(submission_id);
CREATE INDEX IF NOT EXISTS idx_plagiarism_submission ON fact_plagiarism_results(submission_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON fact_audit_events(action);
