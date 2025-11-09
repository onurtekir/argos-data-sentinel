CREATE TABLE IF NOT EXISTS {{ads_runs_table_name}} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT,
    suite_name TEXT,
    suite_description TEXT,
    status TEXT,
    started_at REAL,
    ended_at REAL,
    duration_ms REAL,
    bytes_processed INTEGER,
    cache_hit BOOLEAN,
    validate_first BOOLEAN,
    validate_only BOOLEAN,
    error_count INTEGER,
    extra TEXT
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);