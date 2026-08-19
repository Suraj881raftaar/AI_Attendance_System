"""
Configuration module for AI-Enabled Smart Attendance System.
Handles application constants, directory paths, database configuration, and defaults.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
MODELS_DIR = APP_DIR / "ai" / "models"
FACE_DATA_DIR = DATA_DIR / "face_data"
TESTS_DIR = BASE_DIR / "tests"
DOCS_DIR = BASE_DIR / "docs"

# Database Configuration
DATABASE_PATH = DATA_DIR / "attendance.db"

# Ensure essential data directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
FACE_DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Application Information
APP_NAME = "AI-Enabled Smart Attendance System"
APP_VERSION = "1.0.0"
AUTHOR = "Class 12 Academic Project"

# UI Configuration Defaults
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700
THEME = "dark"           # "dark", "light", "system"
COLOR_THEME = "blue"      # "blue", "dark-blue", "green"

# Camera & AI Defaults
DEFAULT_CAMERA_INDEX = 0
FACE_MATCH_THRESHOLD = 0.6  # Default confidence threshold for face matching
SAMPLES_PER_STUDENT = 5     # Number of face samples captured during registration

def get_db_path() -> Path:
    """Return SQLite database path."""
    return DATABASE_PATH

def ensure_directories():
    """Verify that all required operational directories exist."""
    directories = [DATA_DIR, FACE_DATA_DIR, MODELS_DIR, ASSETS_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    return True
