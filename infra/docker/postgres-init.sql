CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS workspaces (
    workspace_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    data_use_policy TEXT NOT NULL DEFAULT 'customer_private',
    retention_days INTEGER NOT NULL DEFAULT 365,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    content_type TEXT NOT NULL,
    document_type TEXT,
    jurisdiction TEXT,
    domain TEXT,
    source_uri TEXT,
    status TEXT NOT NULL DEFAULT 'uploaded',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS document_versions (
    document_version_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    storage_uri TEXT,
    source_hash TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_to TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS evidence_chunks (
    chunk_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    document_version_id TEXT NOT NULL REFERENCES document_versions(document_version_id) ON DELETE CASCADE,
    workspace_id TEXT NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    content_hash TEXT NOT NULL,
    section_path TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    page_number INTEGER,
    text TEXT NOT NULL,
    embedding_model TEXT,
    embedding_vector vector(1024),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_to TIMESTAMPTZ,
    UNIQUE (workspace_id, document_version_id, content_hash)
);

CREATE INDEX IF NOT EXISTS evidence_chunks_workspace_idx ON evidence_chunks(workspace_id);
CREATE INDEX IF NOT EXISTS evidence_chunks_content_hash_idx ON evidence_chunks(content_hash);

CREATE TABLE IF NOT EXISTS legal_sources (
    source_id TEXT PRIMARY KEY,
    jurisdiction TEXT NOT NULL,
    title TEXT NOT NULL,
    source_uri TEXT,
    version TEXT,
    effective_date DATE,
    metadata JSONB NOT NULL DEFAULT '{}'::JSONB
);

CREATE TABLE IF NOT EXISTS rule_packs (
    rule_pack_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    jurisdiction TEXT NOT NULL,
    domain TEXT NOT NULL,
    version TEXT NOT NULL,
    body JSONB NOT NULL,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS compliance_reviews (
    review_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    rule_pack_id TEXT NOT NULL REFERENCES rule_packs(rule_pack_id),
    answers JSONB NOT NULL DEFAULT '{}'::JSONB,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS findings (
    finding_id TEXT PRIMARY KEY,
    review_id TEXT NOT NULL REFERENCES compliance_reviews(review_id) ON DELETE CASCADE,
    obligation_id TEXT NOT NULL,
    status TEXT NOT NULL,
    summary TEXT NOT NULL,
    citation_chunk_ids TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    reviewer_status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    external_id TEXT NOT NULL,
    source TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    category TEXT,
    priority TEXT,
    duplicate_cluster_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (workspace_id, external_id)
);

CREATE TABLE IF NOT EXISTS ai_traces (
    request_id TEXT PRIMARY KEY,
    workspace_id TEXT REFERENCES workspaces(workspace_id) ON DELETE SET NULL,
    model_provider TEXT NOT NULL,
    model_name TEXT NOT NULL,
    model_route TEXT NOT NULL,
    model_config_version TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    latency_ms INTEGER,
    estimated_cost NUMERIC(12, 6),
    status TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS eval_cases (
    case_id TEXT PRIMARY KEY,
    project TEXT NOT NULL,
    input_reference TEXT NOT NULL,
    expected_output_reference TEXT,
    actual_output_reference TEXT,
    model_provider TEXT,
    model_name TEXT,
    prompt_version TEXT,
    judge_model_provider TEXT,
    judge_model_name TEXT,
    judge_rubric_version TEXT,
    score_type TEXT,
    judge_reasoning TEXT,
    schema_validity BOOLEAN,
    evidence_correctness BOOLEAN,
    citation_correctness BOOLEAN,
    latency_ms INTEGER,
    estimated_cost NUMERIC(12, 6),
    pass_fail BOOLEAN,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS data_use_exclusions (
    exclusion_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    document_id TEXT REFERENCES documents(document_id) ON DELETE CASCADE,
    review_id TEXT,
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    queue TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    payload JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO workspaces (workspace_id, name)
VALUES ('ws-demo', 'Demo workspace')
ON CONFLICT (workspace_id) DO NOTHING;
