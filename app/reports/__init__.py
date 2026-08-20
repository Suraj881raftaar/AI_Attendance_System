"""
Reports & Data Export package for AI-Enabled Smart Attendance System.
Exposes attendance searching, multi-criteria filtering, student analytics,
authorized manual corrections, and CSV/Excel export features.
"""

from app.reports.service import (
    search_attendance_records,
    get_student_attendance_summary,
    correct_attendance_record,
)
from app.reports.exporter import (
    export_attendance_csv,
    export_attendance_excel,
)

__all__ = [
    "search_attendance_records",
    "get_student_attendance_summary",
    "correct_attendance_record",
    "export_attendance_csv",
    "export_attendance_excel",
]
