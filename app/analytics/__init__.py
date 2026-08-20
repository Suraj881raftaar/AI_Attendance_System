"""
Visual Analytics package for AI-Enabled Smart Attendance System.
Exposes daily attendance trends, status distributions, monthly trends, and student risk categories.
"""

from app.analytics.service import (
    get_daily_attendance_trend,
    get_status_distribution,
    get_monthly_attendance_trend,
    get_student_performance_distribution,
)

__all__ = [
    "get_daily_attendance_trend",
    "get_status_distribution",
    "get_monthly_attendance_trend",
    "get_student_performance_distribution",
]
