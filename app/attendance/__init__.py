"""
Attendance package for AI-Enabled Smart Attendance System.
Exposes automatic recognition processing, today's attendance summary, and manual attendance recording.
"""

from app.attendance.service import (
    process_recognition_frame,
    get_today_attendance_summary,
    record_manual_attendance,
    get_recognition_pipeline,
)

__all__ = [
    "process_recognition_frame",
    "get_today_attendance_summary",
    "record_manual_attendance",
    "get_recognition_pipeline",
]
