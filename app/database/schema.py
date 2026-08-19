"""
Database schema definition and initialization for AI-Enabled Smart Attendance System.
Creates tables, default settings, and schema versioning idempotently.
"""

import logging
from pathlib import Path
from typing import Optional, Union

from app.database.connection import get_db_connection

logger = logging.getLogger(__name__)

CURRENT_SCHEMA_VERSION = 1

SCHEMA_SQL = """
-- Schema Information Table
CREATE TABLE IF NOT EXISTS schema_info (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students Table
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    roll_number TEXT UNIQUE,
    name TEXT NOT NULL,
    class_name TEXT NOT NULL,
    section TEXT NOT NULL,
    phone TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Application Users Table (Teachers / Admins)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'teacher',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Attendance Table
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    attendance_date TEXT NOT NULL,
    attendance_time TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Present',
    recognition_method TEXT NOT NULL DEFAULT 'automatic',
    confidence_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
    UNIQUE (student_id, attendance_date)
);

-- Face Data Table (Model Agnostic / Flexible AI Representation)
CREATE TABLE IF NOT EXISTS face_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    model_identifier TEXT NOT NULL,
    encoding_data TEXT NOT NULL,
    data_format TEXT NOT NULL DEFAULT 'json',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
);

-- Application Settings Table
CREATE TABLE IF NOT EXISTS application_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

DEFAULT_SETTINGS = [
    ("school_name", "AI Smart Academy", "Name of the educational institution"),
    ("recognition_threshold", "0.60", "Minimum confidence score for face recognition match"),
    ("duplicate_check_rule", "one_per_day", "Duplicate attendance restriction rule"),
    ("default_camera_index", "0", "Default webcam device index"),
    ("app_theme", "dark", "UI theme preference"),
]


def initialize_database(db_path: Optional[Union[str, Path]] = None) -> bool:
    """
    Initialize SQLite database tables, default settings, and schema version.
    This operation is safe to run repeatedly (idempotent).
    
    :param db_path: Optional path to SQLite database file or :memory:.
    :return: True on success.
    """
    try:
        with get_db_connection(db_path) as conn:
            # Execute DDL statements
            conn.executescript(SCHEMA_SQL)

            # Record schema version if not recorded
            conn.execute(
                "INSERT OR IGNORE INTO schema_info (version) VALUES (?)",
                (CURRENT_SCHEMA_VERSION,)
            )

            # Seed default application settings idempotently
            for key, value, desc in DEFAULT_SETTINGS:
                conn.execute(
                    "INSERT OR IGNORE INTO application_settings (key, value, description) VALUES (?, ?, ?)",
                    (key, value, desc)
                )

        logger.info("Database schema initialization completed successfully.")
        return True
    except Exception as e:
        logger.error(f"Database schema initialization failed: {e}")
        raise
