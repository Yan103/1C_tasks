-- Схема для БД, в которую будут записывать дела

CREATE TABLE IF NOT EXISTS cases (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL CHECK (length(btrim(title)) > 0),
    description TEXT NOT NULL DEFAULT '',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'closed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMPTZ,
    CONSTRAINT cases_dates_valid CHECK (end_date >= start_date),
    CONSTRAINT cases_closed_timestamp_valid CHECK (
        (status = 'closed' AND closed_at IS NOT NULL)
        OR (status = 'open' AND closed_at IS NULL)
    )
);

CREATE TABLE IF NOT EXISTS comments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    case_id BIGINT NOT NULL
        REFERENCES cases(id) ON DELETE RESTRICT,
    text TEXT NOT NULL CHECK (length(btrim(text)) > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cases_dates
    ON cases (start_date, end_date);

CREATE INDEX IF NOT EXISTS idx_cases_status_start
    ON cases (status, start_date);

CREATE INDEX IF NOT EXISTS idx_comments_case_created
    ON comments (case_id, created_at DESC, id DESC);
