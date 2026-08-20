"""
Management Dashboard Service Layer for AI-Enabled Smart Attendance System.
Enforces backend RBAC authorization, computes live summary metrics from SQLite database,
and retrieves formatted recent attendance activity logs.
"""

from datetime import date
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.auth import get_session
from app.database import (
    list_students,
    get_student_by_id,
    get_attendance_by_date,
    list_recent_attendance,
)

logger = logging.getLogger(__name__)


def _require_authenticated_user() -> Dict[str, Any]:
    """Ensure an active user session exists, raising PermissionError if unauthenticated."""
    session = get_session()
    if not session.is_logged_in():
        raise PermissionError("Authentication required to access dashboard metrics.")
    return session.get_current_user()  # type: ignore


def get_dashboard_metrics(db_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Compute real-time summary statistics and recent attendance logs for the dashboard.

    - TOTAL STUDENTS: Count of active registered students only.
    - PRESENT TODAY: Count of unique active students marked Present for today's local date (YYYY-MM-DD).
    - ABSENT TODAY: Active Students - Present Today (never negative).
    - ATTENDANCE %: Present Today / Active Students * 100 (safely 0.0% if zero active students).
    - RECENT ACTIVITY: Latest attendance records with student metadata.

    :param db_path: Optional SQLite database path override.
    :return: Structured dictionary payload containing all dashboard metrics.
    :raises PermissionError: If session is unauthenticated.
    """
    _require_authenticated_user()

    try:
        # 1. Total active registered students
        active_students = list_students(active_only=True, db_path=db_path)
        total_active_count = len(active_students)
        active_student_ids = {s["id"] for s in active_students}

        # 2. Today's date (local date YYYY-MM-DD)
        today_str = date.today().isoformat()
        today_records = get_attendance_by_date(today_str, db_path=db_path)

        # Count unique active students marked Present today
        present_student_ids = {
            rec["student_id"]
            for rec in today_records
            if rec.get("status") == "Present" and rec.get("student_id") in active_student_ids
        }
        present_count = len(present_student_ids)

        # 3. Absent count today (never negative)
        absent_count = max(0, total_active_count - present_count)

        # 4. Attendance percentage (safe zero-division protection)
        if total_active_count > 0:
            percentage = round((present_count / total_active_count) * 100.0, 2)
        else:
            percentage = 0.0

        # 5. Recent attendance activity log (top 10 latest)
        raw_recent = list_recent_attendance(limit=10, db_path=db_path)
        recent_activity: List[Dict[str, Any]] = []

        for rec in raw_recent:
            student_id = rec.get("student_id")
            student = get_student_by_id(student_id, db_path=db_path) if student_id else None

            # Student metadata
            s_name = student["name"] if student else "Unknown"
            s_code = student["student_id"] if student else "-"
            c_name = student.get("class_name", "") if student else ""
            sec = student.get("section", "") if student else ""
            class_sec = f"{c_name}-{sec}".strip("-") if (c_name or sec) else "-"

            activity_item = {
                "attendance_id": rec.get("id"),
                "student_id": student_id,
                "student_name": s_name,
                "student_code": s_code,
                "class_section": class_sec,
                "attendance_date": rec.get("attendance_date"),
                "attendance_time": rec.get("attendance_time"),
                "status": rec.get("status", "Present"),
                "recognition_method": rec.get("recognition_method", "automatic"),
            }
            recent_activity.append(activity_item)

        return {
            "date": today_str,
            "total_students": total_active_count,
            "present_today": present_count,
            "absent_today": absent_count,
            "attendance_percentage": percentage,
            "recent_activity": recent_activity,
        }

    except Exception as e:
        logger.error(f"Error gathering dashboard metrics: {e}")
        # Return graceful zero payload on error
        return {
            "date": date.today().isoformat(),
            "total_students": 0,
            "present_today": 0,
            "absent_today": 0,
            "attendance_percentage": 0.0,
            "recent_activity": [],
            "error": str(e),
        }
