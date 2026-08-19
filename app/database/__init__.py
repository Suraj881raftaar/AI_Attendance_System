"""
Database package for AI-Enabled Smart Attendance System.
Exposes database initialization, connection management, and data access repositories.
"""

from app.database.connection import get_connection, get_db_connection
from app.database.schema import initialize_database, CURRENT_SCHEMA_VERSION
from app.database.repository import (
    # Students
    create_student,
    get_student_by_id,
    get_student_by_student_id,
    list_students,
    update_student,
    deactivate_student,
    # Users
    create_user,
    get_user_by_username,
    get_user_by_id,
    update_user_status,
    update_user_password,
    list_users,
    count_users,
    # Attendance
    create_attendance,
    check_duplicate_attendance,
    get_attendance_by_student,
    get_attendance_by_date,
    list_recent_attendance,
    # Face Data
    create_or_update_face_data,
    get_face_data_by_student,
    deactivate_face_data,
    # Settings
    get_setting,
    set_setting,
    get_all_settings,
)

__all__ = [
    "get_connection",
    "get_db_connection",
    "initialize_database",
    "CURRENT_SCHEMA_VERSION",
    "create_student",
    "get_student_by_id",
    "get_student_by_student_id",
    "list_students",
    "update_student",
    "deactivate_student",
    "create_user",
    "get_user_by_username",
    "get_user_by_id",
    "update_user_status",
    "update_user_password",
    "list_users",
    "count_users",
    "create_attendance",
    "check_duplicate_attendance",
    "get_attendance_by_student",
    "get_attendance_by_date",
    "list_recent_attendance",
    "create_or_update_face_data",
    "get_face_data_by_student",
    "deactivate_face_data",
    "get_setting",
    "set_setting",
    "get_all_settings",
]
