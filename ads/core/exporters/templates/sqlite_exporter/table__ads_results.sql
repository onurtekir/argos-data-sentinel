CREATE TABLE IF NOT EXISTS {{ads_results_table_name}} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    check_name TEXT,
    check_description TEXT,
    check_params TEXT,
    status TEXT,
    severity TEXT,
    value REAL,
    threshold_lower REAL,
    threshold_upper REAL,
    message TEXT,
    FOREIGN KEY(run_id) REFERENCES runs(id)
);