"""
AI Attendance Engine Service Layer for AI-Enabled Smart Attendance System.
Enforces backend RBAC authorization, coordinates real-time recognition, 10s cooldown tracking,
duplicate attendance prevention, inactive student protection, and automatic/manual attendance creation.
"""

from datetime import datetime, date
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import cv2
import numpy as np

from app.config import FACE_MATCH_THRESHOLD
from app.auth import get_session
from app.database import (
    get_student_by_id,
    list_students,
    create_attendance,
    check_duplicate_attendance,
    get_attendance_by_date,
    list_recent_attendance,
)
from app.ai.pipeline import AIRecognitionPipeline

logger = logging.getLogger(__name__)

# Global or module-level singleton instance for AI Recognition Pipeline
_PIPELINE_INSTANCE: Optional[AIRecognitionPipeline] = None


def get_recognition_pipeline() -> AIRecognitionPipeline:
    """Get or initialize the shared AIRecognitionPipeline instance."""
    global _PIPELINE_INSTANCE
    if _PIPELINE_INSTANCE is None:
        _PIPELINE_INSTANCE = AIRecognitionPipeline()
    return _PIPELINE_INSTANCE


def _require_authenticated_user() -> Dict[str, Any]:
    """Ensure an active user session exists, raising PermissionError if unauthenticated."""
    session = get_session()
    if not session.is_logged_in():
        raise PermissionError("Authentication required to perform attendance operations.")
    return session.get_current_user()  # type: ignore


def process_recognition_frame(
    frame: np.ndarray,
    mark_attendance: bool = True,
    pipeline: Optional[AIRecognitionPipeline] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
    """
    Process a video or image frame through the AI Recognition Engine,
    drawing bounding boxes and optionally recording automatic attendance.

    :param frame: BGR numpy image frame.
    :param mark_attendance: If True, automatically creates attendance records for valid matches.
    :param pipeline: Optional AIRecognitionPipeline override.
    :param db_path: Optional SQLite database path override.
    :return: Tuple of (annotated BGR frame, list of recognition event dicts).
    :raises PermissionError: If unauthenticated.
    """
    _require_authenticated_user()

    if frame is None or frame.size == 0:
        return frame, []

    pipe = pipeline or get_recognition_pipeline()

    # Process frame through Stage 4 AI pipeline
    raw_results, annotated_frame = pipe.process_frame(
        frame=frame,
        enrolled_cache=None,
    )

    events: List[Dict[str, Any]] = []
    current_date_str = date.today().isoformat()
    current_time_str = datetime.now().strftime("%H:%M:%S")

    for res in raw_results:
        sim_score = res.similarity_score
        # Check if match meets confidence threshold
        if res.is_known and res.student_id is not None and sim_score >= FACE_MATCH_THRESHOLD:
            student_id = res.student_id
            student = get_student_by_id(student_id, db_path=db_path)

            if not student:
                event = {
                    "timestamp": current_time_str,
                    "status": "error",
                    "student_id": student_id,
                    "student_name": res.student_name,
                    "similarity": sim_score,
                    "message": f"Student ID {student_id} not found in database.",
                }
                events.append(event)
                continue

            # Inactive student check
            if student.get("status") != "active":
                event = {
                    "timestamp": current_time_str,
                    "status": "inactive_rejected",
                    "student_id": student_id,
                    "student_name": student["name"],
                    "student_code": student["student_id"],
                    "similarity": sim_score,
                    "message": f"Inactive student '{student['name']}' rejected.",
                }
                events.append(event)
                logger.info(f"Attendance rejected: Student '{student['name']}' (ID {student_id}) is inactive.")
                continue

            # Check in-memory pipeline cooldown
            last_t = pipe._last_recognized.get(student_id, 0.0)
            if (time.time() - last_t) < pipe.cooldown_seconds:
                event = {
                    "timestamp": current_time_str,
                    "status": "cooldown_skipped",
                    "student_id": student_id,
                    "student_name": student["name"],
                    "student_code": student["student_id"],
                    "similarity": sim_score,
                    "message": f"Recognized: {student['name']} (Already recognized within cooldown)",
                }
                events.append(event)
                continue

            # Check database duplicate attendance for today
            is_duplicate = check_duplicate_attendance(student_id, current_date_str, db_path=db_path)
            if is_duplicate:
                pipe._last_recognized[student_id] = time.time()
                event = {
                    "timestamp": current_time_str,
                    "status": "already_marked",
                    "student_id": student_id,
                    "student_name": student["name"],
                    "student_code": student["student_id"],
                    "similarity": sim_score,
                    "message": f"Recognized: {student['name']} (Already marked Present today)",
                }
                events.append(event)
                continue

            # Mark attendance if requested
            if mark_attendance:
                try:
                    att_rec = create_attendance(
                        student_id=student_id,
                        attendance_date=current_date_str,
                        attendance_time=current_time_str,
                        status="Present",
                        recognition_method="automatic",
                        confidence_score=float(sim_score),
                        db_path=db_path,
                    )
                    pipe._last_recognized[student_id] = time.time()
                    event = {
                        "timestamp": current_time_str,
                        "status": "attendance_created",
                        "attendance_id": att_rec["id"],
                        "student_id": student_id,
                        "student_name": student["name"],
                        "student_code": student["student_id"],
                        "similarity": sim_score,
                        "message": f"Marked Present: {student['name']} [{student['student_id']}] (Conf: {sim_score:.2f})",
                    }
                    events.append(event)
                    logger.info(f"Attendance recorded: {student['name']} (ID {student_id}) marked Present.")
                except ValueError:
                    # Database unique constraint prevented duplicate
                    pipe._last_recognized[student_id] = time.time()
                    event = {
                        "timestamp": current_time_str,
                        "status": "already_marked",
                        "student_id": student_id,
                        "student_name": student["name"],
                        "student_code": student["student_id"],
                        "similarity": sim_score,
                        "message": f"Recognized: {student['name']} (Already marked Present today)",
                    }
                    events.append(event)
        else:
            # Unknown Face
            event = {
                "timestamp": current_time_str,
                "status": "unknown",
                "student_id": None,
                "student_name": "UNKNOWN",
                "similarity": float(sim_score) if sim_score else 0.0,
                "message": "Unknown face detected",
            }
            events.append(event)

    return annotated_frame, events


def get_today_attendance_summary(db_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Query summary statistics for today's attendance.

    :param db_path: Optional SQLite database path override.
    :return: Dict containing total students, present count, absent count, and attendance percentage.
    """
    _require_authenticated_user()

    all_students = list_students(active_only=True, db_path=db_path)
    total_students = len(all_students)

    today_str = date.today().isoformat()
    today_records = get_attendance_by_date(today_str, db_path=db_path)

    present_student_ids = {rec["student_id"] for rec in today_records if rec["status"] == "Present"}
    present_count = len(present_student_ids)
    absent_count = max(0, total_students - present_count)
    percentage = (present_count / total_students * 100.0) if total_students > 0 else 0.0

    return {
        "date": today_str,
        "total_students": total_students,
        "present_count": present_count,
        "absent_count": absent_count,
        "attendance_percentage": round(percentage, 2),
    }


def record_manual_attendance(
    student_id: int,
    attendance_date: Optional[str] = None,
    attendance_time: Optional[str] = None,
    status: str = "Present",
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Manually record or update attendance for a student (authorized manual override).

    :param student_id: Target student ID.
    :param attendance_date: Date string YYYY-MM-DD (defaults to today).
    :param attendance_time: Time string HH:MM:SS (defaults to now).
    :param status: Attendance status ('Present', 'Absent', 'Late', 'Excused').
    :param db_path: Optional SQLite database path override.
    :return: Attendance record dict.
    :raises PermissionError: If unauthenticated.
    """
    _require_authenticated_user()

    student = get_student_by_id(student_id, db_path=db_path)
    if not student:
        raise ValueError(f"Student with ID {student_id} does not exist.")

    rec_date = attendance_date or date.today().isoformat()
    rec_time = attendance_time or datetime.now().strftime("%H:%M:%S")

    return create_attendance(
        student_id=student_id,
        attendance_date=rec_date,
        attendance_time=rec_time,
        status=status,
        recognition_method="manual",
        confidence_score=None,
        db_path=db_path,
    )
