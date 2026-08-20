"""
Comprehensive Stage 9 Automated Test Suite for Visual Analytics & Chart Renderer System.
Tests authentication, RBAC authorization, daily attendance trends, status distributions,
monthly trends, student performance categorization (>90%, 75-90%, <75%), boundary handling,
inactive student exclusion, chart renderer figure creation, and security.
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
from app.analytics import (
    get_daily_attendance_trend,
    get_status_distribution,
    get_monthly_attendance_trend,
    get_student_performance_distribution,
)
from app.analytics.chart_renderer import (
    create_daily_trend_figure,
    create_status_distribution_figure,
    create_monthly_trend_figure,
    create_student_performance_figure,
    cleanup_figure_canvas,
)


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
    """Authenticate session as admin/teacher for RBAC testing."""
    session = get_session()
    session.start_session({"id": 1, "username": "admin_test", "role": "admin"})
    yield session
    session.clear_session()


# ============================================================================
# 1. AUTHENTICATION & RBAC TESTS
# ============================================================================

def test_analytics_unauthenticated(temp_db):
    """Verify analytics service functions throw PermissionError when unauthenticated."""
    session = get_session()
    session.clear_session()

    with pytest.raises(PermissionError):
        get_daily_attendance_trend(db_path=temp_db)

    with pytest.raises(PermissionError):
        get_status_distribution(db_path=temp_db)

    with pytest.raises(PermissionError):
        get_monthly_attendance_trend(db_path=temp_db)

    with pytest.raises(PermissionError):
        get_student_performance_distribution(db_path=temp_db)


# ============================================================================
# 2. DAILY ATTENDANCE TREND TESTS
# ============================================================================

def test_daily_attendance_trend_calculation(temp_db, auth_session):
    """Test daily attendance trend aggregation over 7 days."""
    s1 = create_student("STU-901", "Alice Trend", "12", "A", db_path=temp_db)
    today_str = date.today().isoformat()

    create_attendance(s1["id"], today_str, "09:00:00", status="Present", db_path=temp_db)

    trend = get_daily_attendance_trend(days=7, db_path=temp_db)

    assert trend["days"] == 7
    assert len(trend["dates"]) == 7
    assert len(trend["present_counts"]) == 7
    assert len(trend["absent_counts"]) == 7
    assert trend["present_counts"][-1] == 1  # Today's present count is 1


def test_daily_trend_empty_database(temp_db, auth_session):
    """Verify daily trend handles empty database without crashing."""
    trend = get_daily_attendance_trend(days=7, db_path=temp_db)

    assert trend["days"] == 7
    assert all(c == 0 for c in trend["present_counts"])
    assert all(c == 0 for c in trend["absent_counts"])


# ============================================================================
# 3. STATUS DISTRIBUTION TESTS
# ============================================================================

def test_status_distribution_calculation(temp_db, auth_session):
    """Test proportional count distribution for a selected date."""
    s1 = create_student("STU-902", "Bob Status", "12", "A", db_path=temp_db)
    s2 = create_student("STU-903", "Charlie Status", "12", "A", db_path=temp_db)
    today_str = date.today().isoformat()

    create_attendance(s1["id"], today_str, "09:00:00", status="Present", db_path=temp_db)
    create_attendance(s2["id"], today_str, "09:15:00", status="Late", db_path=temp_db)

    dist = get_status_distribution(target_date=today_str, db_path=temp_db)

    assert dist["date"] == today_str
    assert dist["distribution"]["Present"] == 1
    assert dist["distribution"]["Late"] == 1
    assert dist["distribution"]["Absent"] == 0


# ============================================================================
# 4. MONTHLY TREND TESTS
# ============================================================================

def test_monthly_attendance_trend_calculation(temp_db, auth_session):
    """Test monthly attendance trend aggregation."""
    s1 = create_student("STU-904", "David Monthly", "12", "B", db_path=temp_db)
    today_str = date.today().isoformat()

    create_attendance(s1["id"], today_str, "09:00:00", status="Present", db_path=temp_db)

    monthly = get_monthly_attendance_trend(months=6, db_path=temp_db)

    assert len(monthly["months"]) == 6
    assert len(monthly["percentages"]) == 6
    assert monthly["percentages"][-1] == 100.0  # 100% attendance this month


# ============================================================================
# 5. STUDENT PERFORMANCE CATEGORIZATION TESTS
# ============================================================================

def test_student_performance_categorization(temp_db, auth_session):
    """Test student risk categorization (>90% Excellent, 75-90% Good, <75% At-Risk)."""
    s_exc = create_student("STU-905", "Excellent Student", "12", "A", db_path=temp_db)
    s_good = create_student("STU-906", "Good Student", "12", "A", db_path=temp_db)
    s_risk = create_student("STU-907", "At-Risk Student", "12", "B", db_path=temp_db)
    s_inact = create_student("STU-908", "Inactive Student", "12", "B", db_path=temp_db)

    deactivate_student(s_inact["id"], db_path=temp_db)

    today_str = date.today().isoformat()

    # Excellent Student: 100% attendance (1/1 Present)
    create_attendance(s_exc["id"], today_str, "09:00:00", status="Present", db_path=temp_db)

    # Good Student: 80% attendance (4/5 Present)
    for i in range(4):
        create_attendance(s_good["id"], f"2026-08-0{i+1}", "09:00:00", status="Present", db_path=temp_db)
    create_attendance(s_good["id"], "2026-08-05", "09:00:00", status="Absent", db_path=temp_db)

    # At-Risk Student: 50% attendance (1/2 Present)
    create_attendance(s_risk["id"], "2026-08-01", "09:00:00", status="Present", db_path=temp_db)
    create_attendance(s_risk["id"], "2026-08-02", "09:00:00", status="Absent", db_path=temp_db)

    perf = get_student_performance_distribution(db_path=temp_db)

    assert perf["total_active_students"] == 3  # Inactive student excluded
    assert perf["categories"]["Excellent (>90%)"] == 1
    assert perf["categories"]["Good (75-90%)"] == 1
    assert perf["categories"]["At-Risk (<75%)"] == 1


# ============================================================================
# 6. CHART RENDERER & FIGURE CLEANUP TESTS
# ============================================================================

def test_chart_renderer_figures_creation(temp_db, auth_session):
    """Verify Matplotlib chart figure creation functions run cleanly."""
    t_data = get_daily_attendance_trend(days=7, db_path=temp_db)
    s_data = get_status_distribution(db_path=temp_db)
    m_data = get_monthly_attendance_trend(months=6, db_path=temp_db)
    p_data = get_student_performance_distribution(db_path=temp_db)

    fig1, _ = create_daily_trend_figure(t_data)
    fig2, _ = create_status_distribution_figure(s_data)
    fig3, _ = create_monthly_trend_figure(m_data)
    fig4, _ = create_student_performance_figure(p_data)

    assert fig1 is not None
    assert fig2 is not None
    assert fig3 is not None
    assert fig4 is not None

    cleanup_figure_canvas(None, fig1)
    cleanup_figure_canvas(None, fig2)
    cleanup_figure_canvas(None, fig3)
    cleanup_figure_canvas(None, fig4)
