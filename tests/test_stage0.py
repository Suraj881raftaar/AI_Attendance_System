"""
Stage 0 verification tests.
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.config import (
    APP_NAME,
    APP_VERSION,
    BASE_DIR as CONFIG_BASE_DIR,
    DATABASE_PATH,
    FACE_DATA_DIR,
    MODELS_DIR,
    ensure_directories,
)
from app.main import main


def test_config_paths():
    """Verify configuration directory and file paths exist and match."""
    assert ensure_directories() is True
    assert CONFIG_BASE_DIR.exists()
    assert FACE_DATA_DIR.exists()
    assert MODELS_DIR.exists()


def test_entry_point():
    """Verify main entry point runs cleanly."""
    result = main()
    assert result == 0
