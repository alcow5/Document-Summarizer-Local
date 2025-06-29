-- Privacy-Focused AI Document Summarizer Database Schema
-- SQLite database for storing document summaries and metadata locally

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Main summaries table
CREATE TABLE IF NOT EXISTS summaries (
    doc_id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_extension TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    summary TEXT NOT NULL,
    insights TEXT,
    template TEXT NOT NULL,
    processing_time REAL,
    token_count INTEGER,
    model_used TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_summaries_created_at ON summaries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_summaries_template ON summaries(template);
CREATE INDEX IF NOT EXISTS idx_summaries_filename ON summaries(filename);

-- Application settings table
CREATE TABLE IF NOT EXISTS app_settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT NOT NULL,
    setting_type TEXT DEFAULT 'string',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model information table
CREATE TABLE IF NOT EXISTS model_info (
    model_id TEXT PRIMARY KEY,
    model_name TEXT NOT NULL,
    version TEXT NOT NULL,
    file_path TEXT,
    file_size INTEGER,
    download_date TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Processing statistics table
CREATE TABLE IF NOT EXISTS processing_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_processed DATE NOT NULL,
    documents_processed INTEGER DEFAULT 0,
    total_processing_time REAL DEFAULT 0.0,
    avg_processing_time REAL DEFAULT 0.0,
    total_tokens INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for statistics queries
CREATE INDEX IF NOT EXISTS idx_stats_date ON processing_stats(date_processed DESC);

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    pref_id INTEGER PRIMARY KEY AUTOINCREMENT,
    preference_key TEXT UNIQUE NOT NULL,
    preference_value TEXT,
    data_type TEXT DEFAULT 'string',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document metadata table (for advanced features)
CREATE TABLE IF NOT EXISTS document_metadata (
    metadata_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id TEXT NOT NULL,
    page_count INTEGER,
    word_count INTEGER,
    language TEXT,
    document_type TEXT,
    extracted_entities TEXT, -- JSON string
    keywords TEXT, -- JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doc_id) REFERENCES summaries(doc_id) ON DELETE CASCADE
);

-- Trigger to update updated_at timestamp on summaries
CREATE TRIGGER IF NOT EXISTS update_summaries_timestamp 
    AFTER UPDATE ON summaries
    FOR EACH ROW
BEGIN
    UPDATE summaries SET updated_at = CURRENT_TIMESTAMP WHERE doc_id = NEW.doc_id;
END;

-- Trigger to update updated_at timestamp on app_settings
CREATE TRIGGER IF NOT EXISTS update_settings_timestamp 
    AFTER UPDATE ON app_settings
    FOR EACH ROW
BEGIN
    UPDATE app_settings SET updated_at = CURRENT_TIMESTAMP WHERE setting_key = NEW.setting_key;
END;

-- Trigger to update updated_at timestamp on user_preferences
CREATE TRIGGER IF NOT EXISTS update_preferences_timestamp 
    AFTER UPDATE ON user_preferences
    FOR EACH ROW
BEGIN
    UPDATE user_preferences SET updated_at = CURRENT_TIMESTAMP WHERE pref_id = NEW.pref_id;
END;

-- Insert default settings
INSERT OR IGNORE INTO app_settings (setting_key, setting_value, setting_type, description) VALUES
    ('max_summaries', '50', 'integer', 'Maximum number of summaries to keep in history'),
    ('auto_cleanup', 'true', 'boolean', 'Automatically cleanup old summaries'),
    ('encryption_enabled', 'true', 'boolean', 'Enable database encryption'),
    ('model_auto_update', 'true', 'boolean', 'Automatically check for model updates'),
    ('last_model_check', '', 'datetime', 'Last time model updates were checked'),
    ('app_version', '1.0.0', 'string', 'Current application version'),
    ('database_version', '1.0.0', 'string', 'Current database schema version');

-- Insert default user preferences
INSERT OR IGNORE INTO user_preferences (preference_key, preference_value, data_type) VALUES
    ('default_template', 'general', 'string'),
    ('max_file_size_mb', '50', 'integer'),
    ('processing_timeout', '300', 'integer'),
    ('ui_theme', 'light', 'string'),
    ('show_processing_details', 'false', 'boolean'),
    ('auto_save_summaries', 'true', 'boolean'),
    ('confirm_delete', 'true', 'boolean');

-- Create view for summary statistics
CREATE VIEW IF NOT EXISTS summary_statistics AS
SELECT 
    COUNT(*) as total_summaries,
    COUNT(CASE WHEN DATE(created_at) >= DATE('now', '-7 days') THEN 1 END) as summaries_this_week,
    COUNT(CASE WHEN DATE(created_at) >= DATE('now', '-30 days') THEN 1 END) as summaries_this_month,
    AVG(processing_time) as avg_processing_time,
    MAX(processing_time) as max_processing_time,
    MIN(processing_time) as min_processing_time,
    SUM(file_size) as total_bytes_processed,
    (SELECT template FROM summaries GROUP BY template ORDER BY COUNT(*) DESC LIMIT 1) as most_used_template,
    (SELECT COUNT(*) FROM summaries GROUP BY template ORDER BY COUNT(*) DESC LIMIT 1) as most_used_template_count
FROM summaries;

-- Create view for recent activity
CREATE VIEW IF NOT EXISTS recent_activity AS
SELECT 
    doc_id,
    filename,
    template,
    processing_time,
    created_at,
    'summary' as activity_type
FROM summaries
WHERE DATE(created_at) >= DATE('now', '-30 days')
ORDER BY created_at DESC
LIMIT 100; 