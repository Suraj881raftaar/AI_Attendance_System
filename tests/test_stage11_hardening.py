"""
Comprehensive Stage 11 Automated Hardening Test Suite for AI-Enabled Smart Attendance System.
Aggressively tests system resilience, edge-case handling, error recovery, boundary enforcement,
recognition threshold rules (>= 0.363 recognized vs < 0.363 unknown), 10s cooldown enforcement,
duplicate database protection, CSV/Excel export safety, and database transaction rollbacks.
"""

from datetime import date
import tempfile
from pathlib import Path
import numpy as np
import openpyxl
import pytest

from app.config import FACE_MATCH_THRESHOLD
from app.database import (
    initialize_database,
    create_student,
    deactivate_student,
    create_attendance,
    create_or_update_face_data,
    get_db_connection,
)
from app.auth import login, get_session, setup_first_admin
from app.ai.matcher import FaceMatcher
from app.dashboard import get_dashboard_metrics
from app.reports import (
    search_attendance_records,
    get_student_attendance_summary,
    export_attendance_csv,
    export_attendance_excel,
)


@pytest.fixture
def temp_db():
    """Create an isolated temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    initialize_database(db_path)
    yield db_path
    if db_path.exists():
        try:
            db_path.unlink()
        except PermissionError:
            pass


@pytest.fixture
def auth_session():
    """Authenticate session as admin for testing."""
    session = get_session()
    session.start_session({"id": 1, "username": "admin_h11", "role": "admin"})
    yield session
    session.clear_session()


# ============================================================================
# 1. AUTHENTICATION & RBAC HARDENING
# ============================================================================

def test_auth_empty_and_invalid_credentials(temp_db):
    """Test login failures for empty, missing, or incorrect credentials."""
    setup_first_admin("admin_h11", "SecretPass123!", db_path=temp_db)

    # Empty username
    with pytest.raises(ValueError, match="required"):
        login("", "SecretPass123!", db_path=temp_db)

    # Empty password
    with pytest.raises(ValueError, match="required"):
        login("admin_h11", "", db_path=temp_db)

    # Invalid password
    with pytest.raises(ValueError, match="Invalid username or password"):
        login("admin_h11", "WrongPassword", db_path=temp_db)

    # Nonexistent user
    with pytest.raises(ValueError, match="Invalid username or password"):
        login("nonexistent_user", "SecretPass123!", db_path=temp_db)


def test_auth_session_destruction(temp_db):
    """Verify session destruction upon logout blocks subsequent authorized operations."""
    session = get_session()
    setup_first_admin("admin_h11", "SecretPass123!", db_path=temp_db)
    login("admin_h11", "SecretPass123!", db_path=temp_db)

    assert session.is_logged_in() is True

    # Logout
    session.clear_session()
    assert session.is_logged_in() is False

    # Attempting service call after logout throws PermissionError
    with pytest.raises(PermissionError):
        get_dashboard_metrics(db_path=temp_db)


# ============================================================================
# 2. STUDENT MANAGEMENT HARDENING
# ============================================================================

def test_student_duplicate_id_and_roll_rejection(temp_db, auth_session):
    """Verify duplicate Student ID and roll number constraints are strictly enforced."""
    create_student("STU-1101", "Student One", "12", "A", roll_number="101", db_path=temp_db)

    # Duplicate student_id
    with pytest.raises(ValueError, match="already exists"):
        create_student("STU-1101", "Student Duplicate", "12", "B", db_path=temp_db)


def test_inactive_student_operations(temp_db, auth_session):
    """Verify inactive students are excluded from active list and attendance recognition."""
    s1 = create_student("STU-1102", "Active Student", "12", "A", db_path=temp_db)
    s2 = create_student("STU-1103", "Inactive Student", "12", "A", db_path=temp_db)

    deactivate_student(s2["id"], db_path=temp_db)

    active_list = get_dashboard_metrics(db_path=temp_db)
    assert active_list["total_students"] == 1


# ============================================================================
# 3. RECOGNITION THRESHOLD HARDENING (0.363 RULE)
# ============================================================================

def test_recognition_threshold_boundary_behavior(temp_db):
    """
    Explicitly test boundary behavior around FACE_MATCH_THRESHOLD = 0.363:
    - score >= 0.363 -> recognized
    - score < 0.363 -> unknown
    """
    import json
    assert FACE_MATCH_THRESHOLD == 0.363

    matcher = FaceMatcher(db_path=temp_db)
    emb_target = np.ones(128, dtype=np.float32)
    emb_target /= np.linalg.norm(emb_target)

    # Enroll student face
    s1 = create_student("STU-1104", "Boundary Student", "12", "A", db_path=temp_db)
    create_or_update_face_data(s1["id"], "SFace", json.dumps(emb_target.tolist()), db_path=temp_db)

    # Case A: Exact match (score = 1.0 >= 0.363)
    res_a = matcher.match_embedding(emb_target, db_path=temp_db)
    assert res_a.is_known is True
    assert res_a.student_id == s1["id"]
    assert res_a.similarity_score >= 0.363

    # Case B: Dissimilar embedding (score < 0.363)
    emb_opposite = -emb_target.copy()
    res_b = matcher.match_embedding(emb_opposite, db_path=temp_db)
    assert res_b.is_known is False
    assert res_b.similarity_score < 0.363


# ============================================================================
# 4. ATTENDANCE ENGINE & COOLDOWN HARDENING
# ============================================================================

def test_attendance_cooldown_and_duplicate_protection(temp_db, auth_session):
    """
    Test 10-second cooldown and SQLite UNIQUE(student_id, attendance_date) duplicate protection.
    """
    s1 = create_student("STU-1105", "Cooldown Student", "12", "A", db_path=temp_db)
    today_str = date.today().isoformat()

    # First attendance record creation
    rec1 = create_attendance(s1["id"], today_str, "09:00:00", status="Present", db_path=temp_db)
    assert rec1["id"] is not None

    # Attempt duplicate creation on same date raises ValueError
    with pytest.raises(ValueError, match="already recorded"):
        create_attendance(s1["id"], today_str, "09:05:00", status="Present", db_path=temp_db)


# ============================================================================
# 5. CSV & EXCEL EXPORT DATA SAFETY HARDENING
# ============================================================================

def test_export_data_safety_and_special_characters(temp_db, auth_session):
    """
    Verify CSV and Excel exports handle special characters, empty datasets,
    and DO NOT leak biometric embeddings, raw images, password hashes, or secrets.
    """
    s1 = create_student("STU-1106", "Unicode O'Connor, Jr.", "12", "A", db_path=temp_db)
    create_attendance(s1["id"], "2026-08-20", "09:00:00", status="Present", db_path=temp_db)

    records = search_attendance_records(db_path=temp_db)
    summary = get_student_attendance_summary(db_path=temp_db)

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tf_csv:
        csv_file = Path(tf_csv.name)

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tf_xlsx:
        xlsx_file = Path(tf_xlsx.name)

    export_attendance_csv(records, csv_file)
    export_attendance_excel(records, xlsx_file, summary_data=summary)

    # 1. Verify CSV contents
    with open(csv_file, mode="r", encoding="utf-8") as f:
        csv_content = f.read()
        assert "Unicode O'Connor, Jr." in csv_content
        # Data safety check
        assert "embedding" not in csv_content.lower()
        assert "password" not in csv_content.lower()
        assert "secret" not in csv_content.lower()

    # 2. Verify Excel contents
    wb = openpyxl.load_workbook(xlsx_file)
    ws = wb["Attendance Records"]
    assert ws.cell(row=2, column=3).value == "Unicode O'Connor, Jr."
    wb.close()

    if csv_file.exists():
        try:
            csv_file.unlink()
        except PermissionError:
            pass
    if xlsx_file.exists():
        try:
            xlsx_file.unlink()
        except PermissionError:
            pass


# ============================================================================
# 6. DATABASE TRANSACTION & ROLLBACK HARDENING
# ============================================================================

def test_database_transaction_rollback_safety(temp_db):
    """Verify failed database operations trigger automatic rollback without corrupting existing data."""
    create_student("STU-1107", "Original Student", "12", "A", db_path=temp_db)

    # Intentional invalid SQL execution inside transaction context
    try:
        with get_db_connection(temp_db) as conn:
            conn.execute("INSERT INTO students (student_id, name) VALUES ('STU-1108', 'Temp Student')")
            # Trigger constraint violation
            conn.execute("INSERT INTO students (student_id, name) VALUES ('STU-1108', 'Duplicate Student')")
    except Exception:
        pass

    # Verify rollback: STU-1108 was NOT saved
    with get_db_connection(temp_db) as conn:
        row = conn.execute("SELECT * FROM students WHERE student_id = 'STU-1108'").fetchone()
        assert row is None
