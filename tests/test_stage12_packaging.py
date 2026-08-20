"""
Comprehensive Stage 12 Automated Packaging & Resource Resolution Test Suite.
Tests PyInstaller sys._MEIPASS resource path resolution, ONNX model manifest presence,
runtime directory auto-creation, database initialization hooks, and single-click launcher.
"""

import sys
import tempfile
from pathlib import Path
import pytest

from app.config import (
    BASE_DIR,
    MODELS_DIR,
    FACE_DETECTION_MODEL_PATH,
    FACE_RECOGNITION_MODEL_PATH,
    get_resource_path,
    ensure_directories,
)
from app.database import initialize_database, get_db_connection


def test_spec_file_and_launcher_presence():
    """Verify build specification, build script, and batch launcher exist."""
    spec_file = BASE_DIR / "ai_attendance_system.spec"
    build_script = BASE_DIR / "build_app.py"
    launcher = BASE_DIR / "run_app.bat"

    assert spec_file.exists()
    assert build_script.exists()
    assert launcher.exists()


def test_model_files_manifest_presence():
    """Verify canonical YuNet and SFace ONNX model files exist in project manifest."""
    assert FACE_DETECTION_MODEL_PATH.exists()
    assert FACE_RECOGNITION_MODEL_PATH.exists()


def test_resource_path_resolution_dev_mode():
    """Verify get_resource_path() in development mode resolves relative to BASE_DIR."""
    res_path = get_resource_path("models")
    assert res_path == MODELS_DIR


def test_resource_path_resolution_frozen_mode(monkeypatch):
    """Test get_resource_path() under simulated PyInstaller frozen execution mode (sys._MEIPASS)."""
    with tempfile.TemporaryDirectory() as tmp_meipass:
        tmp_path = Path(tmp_meipass)
        dummy_model = tmp_path / "models" / "dummy.onnx"
        dummy_model.parent.mkdir(parents=True, exist_ok=True)
        dummy_model.write_text("dummy model data")

        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

        import app.config as config
        monkeypatch.setattr(config, "IS_FROZEN", True)
        monkeypatch.setattr(config, "RESOURCE_ROOT", tmp_path)

        res = config.get_resource_path("models/dummy.onnx")
        assert res == dummy_model
        assert res.exists()


def test_runtime_directory_autocreation():
    """Verify ensure_directories() creates operational data and log directories."""
    assert ensure_directories() is True


def test_database_auto_initialization_on_missing():
    """Verify database auto-initialization hook creates tables safely on missing path."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = Path(tf.name)
    db_path.unlink()  # Ensure database does not exist

    initialize_database(db_path)
    assert db_path.exists()

    with get_db_connection(db_path) as conn:
        tables = [row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        assert "students" in tables
        assert "attendance" in tables
        assert "users" in tables
        assert "face_data" in tables

    if db_path.exists():
        try:
            db_path.unlink()
        except PermissionError:
            pass
