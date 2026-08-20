"""
Attendance Reports Service Layer for AI-Enabled Smart Attendance System.
Enforces backend RBAC authorization, coordinates multi-criteria searching & filtering,
computes student attendance analytics, and handles authorized manual corrections.
"""

from datetime import datetime
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.auth import get_session
from app.database import (
    get_db_connection,
    list_students,
    get_student_by_id,
    update_attendance_record,
)

logger = logging.getLogger(__name__)

VALID_ATTENDANCE_STATUSES = {"Present", "Absent", "Late", "Excused"}


def _require_authenticated_user() -> Dict[str, Any]:
    """Ensure an active user session exists, raising PermissionError if unauthenticated."""
    session = get_session()
    if not session.is_logged_in():
        raise PermissionError("Authentication required to access reports & attendance management.")
    return session.get_current_user()  # type: ignore


def _validate_date_string(date_str: str, param_name: str) -> str:
    """Validate YYYY-MM-DD date string format."""
    clean = (date_str or "").strip()
    if not clean:
        return ""
    try:
        datetime.strptime(clean, "%Y-%m-%d")
        return clean
    except ValueError as e:
        raise ValueError(f"Invalid {param_name} format '{date_str}'. Expected YYYY-MM-DD.") from e


def search_attendance_records(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    student_query: Optional[str] = None,
    class_query: Optional[str] = None,
    status_filter: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """
    Search and filter attendance records based on multi-criteria inputs.

    :param start_date: YYYY-MM-DD start date boundary (inclusive).
    :param end_date: YYYY-MM-DD end date boundary (inclusive).
    :param student_query: Student name or student ID/code search substring.
    :param class_query: Class or section search substring.
    :param status_filter: Attendance status ('Present', 'Absent', 'Late', 'Excused').
    :param db_path: Optional SQLite database path override.
    :return: List of formatted attendance record dicts joined with student metadata.
    :raises PermissionError: If session is unauthenticated.
    :raises ValueError: If date format is invalid.
    """
    _require_authenticated_user()

    clean_start = _validate_date_string(start_date, "start_date") if start_date else ""
    clean_end = _validate_date_string(end_date, "end_date") if end_date else ""

    query = """
        SELECT 
            a.id AS attendance_id,
            a.student_id,
            a.attendance_date,
            a.attendance_time,
            a.status,
            a.recognition_method,
            a.confidence_score,
            s.student_id AS student_code,
            s.name AS student_name,
            s.class_name,
            s.section,
            s.roll_number
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE 1=1
    """
    params: List[Any] = []

    if clean_start:
        query += " AND a.attendance_date >= ?"
        params.append(clean_start)

    if clean_end:
        query += " AND a.attendance_date <= ?"
        params.append(clean_end)

    if status_filter and status_filter.strip() and status_filter.strip().lower() != "all":
        clean_status = status_filter.strip().capitalize()
        if clean_status not in VALID_ATTENDANCE_STATUSES:
            raise ValueError(f"Invalid status filter '{status_filter}'. Must be one of {VALID_ATTENDANCE_STATUSES}.")
        query += " AND LOWER(a.status) = LOWER(?)"
        params.append(clean_status)

    if student_query and student_query.strip():
        sq = f"%{student_query.strip().lower()}%"
        query += " AND (LOWER(s.name) LIKE ? OR LOWER(s.student_id) LIKE ?)"
        params.extend([sq, sq])

    if class_query and class_query.strip():
        cq = f"%{class_query.strip().lower()}%"
        query += " AND (LOWER(s.class_name) LIKE ? OR LOWER(s.section) LIKE ? OR LOWER(s.class_name || '-' || s.section) LIKE ?)"
        params.extend([cq, cq, cq])

    query += " ORDER BY a.attendance_date DESC, a.attendance_time DESC"

    with get_db_connection(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
        results: List[Dict[str, Any]] = []
        for r in rows:
            item = dict(r)
            cname = item.get("class_name") or ""
            sec = item.get("section") or ""
            item["class_section"] = f"{cname}-{sec}".strip("-") if (cname or sec) else "-"
            results.append(item)
        return results


def get_student_attendance_summary(
    student_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """
    Compute per-student attendance summary analytics (total days, present count, absent, late, percentage).

    :param student_id: Optional single student ID filter.
    :param start_date: YYYY-MM-DD start date boundary.
    :param end_date: YYYY-MM-DD end date boundary.
    :param db_path: Optional SQLite database path override.
    :return: List of student analytics summary dicts.
    """
    _require_authenticated_user()

    target_students = []
    if student_id is not None:
        st = get_student_by_id(student_id, db_path=db_path)
        if st:
            target_students.append(st)
    else:
        target_students = list_students(active_only=True, db_path=db_path)

    records = search_attendance_records(start_date=start_date, end_date=end_date, db_path=db_path)

    summaries: List[Dict[str, Any]] = []

    for st in target_students:
        sid = st["id"]
        st_records = [r for r in records if r["student_id"] == sid]

        total_days = len(st_records)
        present_count = len([r for r in st_records if r["status"] == "Present"])
        absent_count = len([r for r in st_records if r["status"] == "Absent"])
        late_count = len([r for r in st_records if r["status"] == "Late"])
        excused_count = len([r for r in st_records if r["status"] == "Excused"])

        # Safe percentage calculation with zero-day division protection
        if total_days > 0:
            percentage = round((present_count / total_days) * 100.0, 2)
        else:
            percentage = 0.0

        cname = st.get("class_name") or ""
        sec = st.get("section") or ""
        class_sec = f"{cname}-{sec}".strip("-") if (cname or sec) else "-"

        summaries.append({
            "student_id": sid,
            "student_code": st["student_id"],
            "student_name": st["name"],
            "class_section": class_sec,
            "total_days": total_days,
            "present_count": present_count,
            "absent_count": absent_count,
            "late_count": late_count,
            "excused_count": excused_count,
            "attendance_percentage": percentage,
        })

    return summaries


def correct_attendance_record(
    attendance_id: int,
    status: Optional[str] = None,
    attendance_time: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Authorized manual attendance record status/time correction.

    :param attendance_id: Target attendance record primary key ID.
    :param status: New status ('Present', 'Absent', 'Late', 'Excused').
    :param attendance_time: Optional new time string 'HH:MM:SS'.
    :param db_path: Optional SQLite database path override.
    :return: Updated attendance record dict.
    :raises PermissionError: If session is unauthenticated.
    :raises ValueError: If record does not exist or status is invalid.
    """
    _require_authenticated_user()

    updated = update_attendance_record(
        attendance_id=attendance_id,
        status=status,
        attendance_time=attendance_time,
        db_path=db_path,
    )

    if not updated:
        raise ValueError(f"Attendance record with ID {attendance_id} does not exist.")

    logger.info(f"Authorized correction applied to attendance ID {attendance_id}: status={status}, time={attendance_time}")
    return updated
