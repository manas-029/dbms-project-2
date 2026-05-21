CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(180) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE profile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES "user"(id) ON DELETE CASCADE,
    phone VARCHAR(30),
    public_username VARCHAR(80),
    location VARCHAR(100),
    privacy_goal VARCHAR(255) DEFAULT 'Reduce public exposure',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE social_account (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    platform VARCHAR(80) NOT NULL,
    username VARCHAR(120) NOT NULL,
    profile_url VARCHAR(255),
    visibility VARCHAR(30) NOT NULL DEFAULT 'Public',
    sensitive_data VARCHAR(255) DEFAULT 'Email, location',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE connected_platform (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    name VARCHAR(120) NOT NULL,
    category VARCHAR(80) NOT NULL,
    data_collected VARCHAR(255) NOT NULL,
    permissions VARCHAR(255) NOT NULL,
    third_party_access BOOLEAN NOT NULL DEFAULT FALSE,
    privacy_setting VARCHAR(30) NOT NULL DEFAULT 'Medium',
    last_activity_date DATE,
    retention_months INTEGER NOT NULL DEFAULT 12,
    breach_found BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE consent (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    platform_name VARCHAR(120) NOT NULL,
    permission VARCHAR(160) NOT NULL,
    purpose VARCHAR(255) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Granted',
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    shared_with VARCHAR(255) DEFAULT 'Internal analytics',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE risk_assessment (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
    level VARCHAR(20) NOT NULL,
    factors TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE alert (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    title VARCHAR(160) NOT NULL,
    message VARCHAR(255) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'Medium',
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    source VARCHAR(80) NOT NULL DEFAULT 'Risk Engine',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE deletion_request (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    platform_name VARCHAR(120) NOT NULL,
    data_type VARCHAR(120) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Pending',
    admin_note VARCHAR(255),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) ON DELETE SET NULL,
    action VARCHAR(160) NOT NULL,
    entity VARCHAR(80) NOT NULL,
    ip_address VARCHAR(60),
    details TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE notification (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    channel VARCHAR(30) NOT NULL DEFAULT 'In-app',
    subject VARCHAR(160) NOT NULL,
    body VARCHAR(255) NOT NULL,
    is_sent BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE analytics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    month VARCHAR(20) NOT NULL,
    exposure_score INTEGER NOT NULL CHECK (exposure_score BETWEEN 0 AND 100),
    risk_score INTEGER NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
    consent_count INTEGER NOT NULL,
    platform_count INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE admin (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES "user"(id) ON DELETE CASCADE,
    department VARCHAR(120) NOT NULL DEFAULT 'Privacy Operations',
    privileges VARCHAR(255) NOT NULL DEFAULT 'users,risks,audit,deletions',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_role ON "user"(role);
CREATE INDEX idx_social_account_user_id ON social_account(user_id);
CREATE INDEX idx_connected_platform_user_id ON connected_platform(user_id);
CREATE INDEX idx_consent_user_id ON consent(user_id);
CREATE INDEX idx_consent_status ON consent(status);
CREATE INDEX idx_risk_assessment_user_id ON risk_assessment(user_id);
CREATE INDEX idx_risk_assessment_level ON risk_assessment(level);
CREATE INDEX idx_alert_user_id ON alert(user_id);
CREATE INDEX idx_alert_severity ON alert(severity);
CREATE INDEX idx_deletion_request_user_id ON deletion_request(user_id);
CREATE INDEX idx_deletion_request_status ON deletion_request(status);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
CREATE INDEX idx_notification_user_id ON notification(user_id);
CREATE INDEX idx_analytics_user_id ON analytics(user_id);
