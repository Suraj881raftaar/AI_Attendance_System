"""
Visual Analytics Service Layer for AI-Enabled Smart Attendance System.
Enforces backend RBAC authorization, aggregates attendance data from SQLite for chart rendering,
and computes daily trends, status distributions, monthly trends, and student risk categories.
"""

from datetime import date, datetime, timedelta
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

from app.auth import get_session
from app.database import (
    get_db_connection,
    list_students,
)
from app.reports.service import get_student_attendance_summary

logger = logging.getLogger(__name__)


def _require_authenticated_user() -> Dict[str, Any]:
    """Ensure an active user session exists, raising PermissionError if unauthenticated."""
    session = get_session()
    if not session.is_logged_in():
        raise PermissionError("Authentication required to access analytics services.")
    return session.get_current_user()  # type: ignore


def get_daily_attendance_trend(
    days: int = 7,
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Compute daily Present vs Absent attendance counts over the past N days (7, 14, or 30 days).

    :param days: Number of past days to analyze (default 7).
    :param db_path: Optional SQLite database path override.
    :return: Dict containing dates list, present_counts list, and absent_counts list.
    :raises PermissionError: If session is unauthenticated.
    """
    _require_authenticated_user()

    if days not in (7, 14, 30):
        days = 7

    today = date.today()
    date_list = [(today - timedelta(days=i)).isoformat() for i in reversed(range(days))]

    # Get active registered students count for reference absent calculation
    active_students = list_students(active_only=True, db_path=db_path)
    total_active = len(active_students)
    active_student_ids = {s["id"] for s in active_students}

    query = """
        SELECT attendance_date, student_id, status
        FROM attendance
        WHERE attendance_date >= ? AND attendance_date <= ?
    """
    params = (date_list[0], date_list[-1])

    records_by_date: Dict[str, Dict[str, int]] = {
        d: {"Present": 0, "Absent": 0, "Late": 0, "Excused": 0} for d in date_list
    }

    with get_db_connection(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
        for r in rows:
            rec_date = r["attendance_date"]
            status = r["status"]
            sid = r["student_id"]
            if rec_date in records_by_date and sid in active_student_ids:
                if status in records_by_date[rec_date]:
                    records_by_date[rec_date][status] += 1

    present_counts = []
    absent_counts = []

    for d in date_list:
        p_count = records_by_date[d]["Present"] + records_by_date[d]["Late"]  # Count Present + Late as present
        # Absent = total active students - present count for that date
        a_count = records_by_date[d]["Absent"]
        if a_count == 0 and total_active > 0:
            a_count = max(0, total_active - p_count)

        present_counts.append(p_count)
        absent_counts.append(a_count)

    return {
        "days": days,
        "dates": date_list,
        "present_counts": present_counts,
        "absent_counts": absent_counts,
    }


def get_status_distribution(
    target_date: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Compute proportional count distribution of attendance statuses (Present, Absent, Late, Excused) for a selected date.

    :param target_date: YYYY-MM-DD date string (defaults to today).
    :param db_path: Optional SQLite database path override.
    :return: Dict containing status count breakdown.
    """
    _require_authenticated_user()

    if not target_date or not target_date.strip():
        target_date = date.today().isoformat()
    else:
        target_date = target_date.strip()

    active_students = list_students(active_only=True, db_path=db_path)
    total_active = len(active_students)
    active_student_ids = {s["id"] for s in active_students}

    query = """
        SELECT status, student_id
        FROM attendance
        WHERE attendance_date = ?
    """

    counts = {"Present": 0, "Absent": 0, "Late": 0, "Excused": 0}
    present_student_ids = set()

    with get_db_connection(db_path) as conn:
        rows = conn.execute(query, (target_date,)).fetchall()
        for r in rows:
            sid = r["student_id"]
            st = r["status"]
            if sid in active_student_ids and st in counts:
                counts[st] += 1
                if st in ("Present", "Late"):
                    present_student_ids.add(sid)

    # Auto-fill unrecorded active students as Absent for today if total_active > present
    if total_active > 0 and len(rows) > 0:
        unrecorded_absent = max(0, total_active - len(present_student_ids) - counts["Absent"] - counts["Excused"])
        counts["Absent"] += unrecorded_absent

    return {
        "date": target_date,
        "total_active_students": total_active,
        "distribution": counts,
        "has_data": len(rows) > 0 or total_active > 0,
    }


def get_monthly_attendance_trend(
    months: int = 6,
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Compute monthly average attendance percentage rates over past M months.

    :param months: Number of past months to aggregate (default 6).
    :param db_path: Optional SQLite database path override.
    :return: Dict containing month_labels list and percentage_values list.
    """
    _require_authenticated_user()

    if months < 1 or months > 12:
        months = 6

    today = date.today()
    month_keys = []
    month_labels = []

    # Generate YYYY-MM month keys
    cur_year = today.year
    cur_month = today.month

    for i in reversed(range(months)):
        m = cur_month - i
        y = cur_year
        while m <= 0:
            m += 12
            y -= 1
        m_key = f"{y:04d}-{m:02d}"
        m_lbl = datetime(y, m, 1).strftime("%b %Y")
        month_keys.append(m_key)
        month_labels.append(m_lbl)

    query = """
        SELECT strftime('%Y-%m', attendance_date) AS month_key, status, COUNT(*) AS count
        FROM attendance
        GROUP BY month_key, status
    """

    month_data: Dict[str, Dict[str, int]] = {k: {"Present": 0, "Total": 0} for k in month_keys}

    with get_db_connection(db_path) as conn:
        rows = conn.execute(query).fetchall()
        for r in rows:
            mk = r["month_key"]
            st = r["status"]
            cnt = r["count"]
            if mk in month_data:
                month_data[mk]["Total"] += cnt
                if st in ("Present", "Late"):
                    month_data[mk]["Present"] += cnt

    percentage_values = []
    for k in month_keys:
        tot = month_data[k]["Total"]
        pres = month_data[k]["Present"]
        if tot > 0:
            pct = round((pres / tot) * 100.0, 1)
        else:
            pct = 0.0
        percentage_values.append(pct)

    return {
        "months": month_labels,
        "percentages": percentage_values,
    }


def get_student_performance_distribution(
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Categorize ACTIVE students according to their attendance rate:
    - Excellent: > 90.0%
    - Good: 75.0% - 90.0% (inclusive)
    - At-Risk: < 75.0%

    :param db_path: Optional SQLite database path override.
    :return: Dict containing category counts and student breakdown list.
    """
    _require_authenticated_user()

    summaries = get_student_attendance_summary(db_path=db_path)

    counts = {
        "Excellent (>90%)": 0,
        "Good (75-90%)": 0,
        "At-Risk (<75%)": 0,
    }
    details = []

    for st in summaries:
        rate = st["attendance_percentage"]

        if rate > 90.0:
            cat = "Excellent (>90%)"
        elif rate >= 75.0:
            cat = "Good (75-90%)"
        else:
            cat = "At-Risk (<75%)"

        counts[cat] += 1
        details.append({
            "student_id": st["student_id"],
            "student_code": st["student_code"],
            "student_name": st["student_name"],
            "class_section": st["class_section"],
            "attendance_percentage": rate,
            "category": cat,
        })

    return {
        "categories": counts,
        "details": details,
        "total_active_students": len(summaries),
    }
