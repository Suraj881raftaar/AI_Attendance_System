"""
Configuration module for AI-Enabled Smart Attendance System.
Handles application constants, directory paths, database configuration, and defaults.
"""

import sys
from pathlib import Path

# PyInstaller Frozen Execution Check
IS_FROZEN = getattr(sys, 'frozen', False)

# Base Paths
if IS_FROZEN:
    # Read-only bundled resource root under PyInstaller
    RESOURCE_ROOT = Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent))
    # Writable user data root (executable directory)
    EXEC_DIR = Path(sys.executable).parent.resolve()
    BASE_DIR = EXEC_DIR
else:
    RESOURCE_ROOT = Path(__file__).resolve().parent.parent
    EXEC_DIR = RESOURCE_ROOT
    BASE_DIR = RESOURCE_ROOT

def get_resource_path(relative_path: str) -> Path:
    """
    Resolve resource paths supporting both Python development mode and PyInstaller frozen mode.
    Read-only resources (models, assets) use sys._MEIPASS when frozen.
    """
    if IS_FROZEN:
        bundled_path = RESOURCE_ROOT / relative_path
        if bundled_path.exists():
            return bundled_path
    return BASE_DIR / relative_path

APP_DIR = BASE_DIR / "app"
DATA_DIR = EXEC_DIR / "data"
LOGS_DIR = EXEC_DIR / "logs"
ASSETS_DIR = get_resource_path("assets")
MODELS_DIR = get_resource_path("models")
FACE_DETECTION_MODEL_DIR = MODELS_DIR / "face_detection"
FACE_RECOGNITION_MODEL_DIR = MODELS_DIR / "face_recognition"
FACE_DETECTION_MODEL_PATH = FACE_DETECTION_MODEL_DIR / "face_detection_yunet_2023mar.onnx"
FACE_RECOGNITION_MODEL_PATH = FACE_RECOGNITION_MODEL_DIR / "face_recognition_sface_2021dec.onnx"
FACE_DATA_DIR = DATA_DIR / "face_data"
TESTS_DIR = BASE_DIR / "tests"
DOCS_DIR = BASE_DIR / "docs"

# Database Configuration
DATABASE_PATH = DATA_DIR / "attendance.db"

# Ensure essential data directories exist safely
DATA_DIR.mkdir(parents=True, exist_ok=True)
FACE_DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
try:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    FACE_DETECTION_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    FACE_RECOGNITION_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

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
FACE_MATCH_THRESHOLD = 0.363  # Stage 4 Cosine Similarity Threshold (0.363)
SAMPLES_PER_STUDENT = 5       # Number of face samples captured during registration
MODEL_IDENTIFIER = "opencv_sface_v1"
EMBEDDING_DIMENSION = 128
MIN_FACE_SIZE = (60, 60)

def get_db_path() -> Path:
    """Return SQLite database path."""
    return DATABASE_PATH

def ensure_directories():
    """Verify that all required operational directories exist."""
    directories = [DATA_DIR, FACE_DATA_DIR, LOGS_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    return True
