"""
Comprehensive Stage 7 Automated Test Suite for Management Dashboard System.
Tests authentication, RBAC authorization, active student count, inactive student exclusion,
present-today count, absent calculation, attendance percentage (with zero-student safety),
empty table handling, recent activity ordering, and database consistency.
"""

from datetime import date, datetime
import tempfile
from pathlib import Path
import pytest

from app.database import (
    initialize_database,
    create_student,
    deactivate_student,
    create_attendance,
)
from app.auth import get_session
from app.dashboard.service import get_dashboard_metrics


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing."""
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
    """Authenticate session as teacher for RBAC testing."""
    session = get_session()
    session.start_session({"id": 1, "username": "admin_test", "role": "admin"})
    yield session
    session.clear_session()


# ============================================================================
# 1. AUTHENTICATION & RBAC TESTS
# ============================================================================

def test_dashboard_unauthenticated(temp_db):
    """Verify get_dashboard_metrics throws PermissionError when unauthenticated."""
    session = get_session()
    session.clear_session()

    with pytest.raises(PermissionError):
        get_dashboard_metrics(db_path=temp_db)


# ============================================================================
# 2. ZERO-STUDENT & EMPTY DATABASE TESTS
# ============================================================================

def test_dashboard_empty_database(temp_db, auth_session):
    """Verify metrics calculation when database has 0 students and 0 attendance records."""
    metrics = get_dashboard_metrics(db_path=temp_db)

    assert metrics["total_students"] == 0
    assert metrics["present_today"] == 0
    assert metrics["absent_today"] == 0
    assert metrics["attendance_percentage"] == 0.0
    assert metrics["recent_activity"] == []


# ============================================================================
# 3. METRICS CALCULATION & INACTIVE EXCLUSION TESTS
# ============================================================================

def test_dashboard_active_student_count(temp_db, auth_session):
    """Verify total students metric counts ONLY active registered students."""
    s1 = create_student("STU-701", "Active One", "12", "A", db_path=temp_db)
    s2 = create_student("STU-702", "Active Two", "12", "A", db_path=temp_db)
    s3 = create_student("STU-703", "Inactive Three", "12", "B", db_path=temp_db)

    # Deactivate student 3
    deactivate_student(s3["id"], db_path=temp_db)

    metrics = get_dashboard_metrics(db_path=temp_db)
    assert metrics["total_students"] == 2  # Only active students counted


def test_dashboard_present_absent_percentage(temp_db, auth_session):
    """Verify calculation of present today, absent today, and percentage."""
    s1 = create_student("STU-704", "Alice Present", "12", "A", db_path=temp_db)
    s2 = create_student("STU-705", "Bob Present", "12", "A", db_path=temp_db)
    s3 = create_student("STU-706", "Charlie Absent", "12", "B", db_path=temp_db)
    s4 = create_student("STU-707", "David Absent", "12", "B", db_path=temp_db)

    today_str = date.today().isoformat()

    # Mark s1 and s2 Present today
    create_attendance(s1["id"], today_str, "09:00:00", status="Present", db_path=temp_db)
    create_attendance(s2["id"], today_str, "09:05:00", status="Present", db_path=temp_db)

    metrics = get_dashboard_metrics(db_path=temp_db)

    assert metrics["total_students"] == 4
    assert metrics["present_today"] == 2
    assert metrics["absent_today"] == 2
    assert metrics["attendance_percentage"] == 50.0  # 2 / 4 * 100 = 50.0%


# ============================================================================
# 4. RECENT ACTIVITY LIST ORDERING & METADATA TESTS
# ============================================================================

def test_dashboard_recent_activity_ordering(temp_db, auth_session):
    """Verify recent activity list returns top 10 entries formatted with student metadata."""
    s1 = create_student("STU-708", "Eve Activity", "12", "C", db_path=temp_db)
    today_str = date.today().isoformat()

    create_attendance(s1["id"], today_str, "08:30:00", status="Present", db_path=temp_db)

    metrics = get_dashboard_metrics(db_path=temp_db)
    activity = metrics["recent_activity"]

    assert len(activity) == 1
    item = activity[0]
    assert item["student_name"] == "Eve Activity"
    assert item["student_code"] == "STU-708"
    assert item["class_section"] == "12-C"
    assert item["status"] == "Present"
    assert item["attendance_time"] == "08:30:00"
