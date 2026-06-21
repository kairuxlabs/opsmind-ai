CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_query TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'planning',
    state JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_logs (
    id SERIAL PRIMARY KEY,
    workflow_id TEXT,
    agent_name VARCHAR(100),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    latency_ms INTEGER DEFAULT 0,
    token_usage INTEGER DEFAULT 0,
    output JSONB DEFAULT '{}',
    error TEXT
);

CREATE TABLE IF NOT EXISTS memory_store (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
