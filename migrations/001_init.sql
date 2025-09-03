-- idempotent creation
CREATE TABLE IF NOT EXISTS events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type      TEXT,                   -- wedding, community_event, private_function, sports, other
    applicant_name  TEXT NOT NULL,
    applicant_email TEXT NOT NULL,
    applicant_phone TEXT NOT NULL,

    event_name      TEXT NOT NULL,
    location        TEXT NOT NULL,
    start_date      TEXT NOT NULL,          -- ISO date or datetime
    end_date        TEXT NOT NULL,          -- ISO date or datetime

    attendance      INTEGER DEFAULT 0,
    alcohol         TEXT CHECK (alcohol IN ('Yes','No')) DEFAULT 'No',
    high_risk       TEXT CHECK (high_risk IN ('Yes','No')) DEFAULT 'No',
    traffic_mgmt    TEXT CHECK (traffic_mgmt IN ('Yes','No')) DEFAULT 'No',
    vehicle_access  TEXT CHECK (vehicle_access IN ('Yes','No')) DEFAULT 'No',
    amplified_sound TEXT CHECK (amplified_sound IN ('Yes','No')) DEFAULT 'No',
    noise_level     INTEGER DEFAULT 0,
    total_days      INTEGER DEFAULT 1,
    notes           TEXT,

    classification  TEXT CHECK (classification IN ('Self-assessable','Assessable')) NOT NULL,
    status          TEXT CHECK (status IN ('Pending','Approved','Rejected')) NOT NULL DEFAULT 'Pending',

    created_at      TEXT NOT NULL
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_events_created     ON events (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_class       ON events (classification);
CREATE INDEX IF NOT EXISTS idx_events_status      ON events (status);
CREATE INDEX IF NOT EXISTS idx_events_dates       ON events (start_date, end_date);
