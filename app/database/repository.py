"""
Repository and data access layer for AI-Enabled Smart Attendance System.
Provides validated, parameterized data access functions for Students, Users, Attendance, Face Data, and Settings.
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.database.connection import get_db_connection

logger = logging.getLogger(__name__)


# ============================================================================
# STUDENT REPOSITORY
# ============================================================================

def create_student(
    student_id: str,
    name: str,
    class_name: str,
    section: str,
    roll_number: Optional[str] = None,
    phone: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Create a new student record.
    
    :raises ValueError: If validation fails or duplicate student_id/roll_number.
    """
    # Input Validation
    student_id = (student_id or "").strip()
    name = (name or "").strip()
    class_name = (class_name or "").strip()
    section = (section or "").strip()
    roll_number = roll_number.strip() if roll_number else None
    phone = phone.strip() if phone else None

    if not student_id:
        raise ValueError("Student ID cannot be empty.")
    if not name:
        raise ValueError("Student name cannot be empty.")
    if not class_name:
        raise ValueError("Class name cannot be empty.")
    if not section:
        raise ValueError("Section cannot be empty.")

    query = """
        INSERT INTO students (student_id, roll_number, name, class_name, section, phone)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (student_id, roll_number, name, class_name, section, phone))
            new_id = cursor.lastrowid
            row = conn.execute("SELECT * FROM students WHERE id = ?", (new_id,)).fetchone()
            return dict(row)
    except sqlite3.IntegrityError as e:
        logger.warning(f"Failed to create student '{student_id}': Integrity Error ({e})")
        raise ValueError(f"Student ID '{student_id}' or Roll Number '{roll_number}' already exists.") from e


def get_student_by_id(id_val: int, db_path: Optional[Union[str, Path]] = None) -> Optional[Dict[str, Any]]:
    """Retrieve student record by primary key ID."""
    query = "SELECT * FROM students WHERE id = ?"
    with get_db_connection(db_path) as conn:
        row = conn.execute(query, (id_val,)).fetchone()
        return dict(row) if row else None


def get_student_by_student_id(student_id: str, db_path: Optional[Union[str, Path]] = None) -> Optional[Dict[str, Any]]:
    """Retrieve student record by unique string student_id."""
    student_id = (student_id or "").strip()
    if not student_id:
        return None
    query = "SELECT * FROM students WHERE student_id = ?"
    with get_db_connection(db_path) as conn:
        row = conn.execute(query, (student_id,)).fetchone()
        return dict(row) if row else None


def list_students(active_only: bool = True, db_path: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
    """List all students, optionally filtering by active status."""
    if active_only:
        query = "SELECT * FROM students WHERE status = 'active' ORDER BY name ASC"
    else:
        query = "SELECT * FROM students ORDER BY name ASC"
    with get_db_connection(db_path) as conn:
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]


def search_students(
    query_str: str,
    active_only: bool = True,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """
    Search students by student_id, name, or roll_number using case-insensitive LIKE queries.
    
    :param query_str: Search term string.
    :param active_only: If True, filter by active status.
    :param db_path: Optional SQLite database path.
    :return: List of matching student records.
    """
    query_str = (query_str or "").strip()
    if not query_str:
        return list_students(active_only=active_only, db_path=db_path)

    pattern = f"%{query_str}%"

    if active_only:
        sql = """
            SELECT * FROM students
            WHERE (student_id LIKE ? OR name LIKE ? OR roll_number LIKE ?)
              AND status = 'active'
            ORDER BY name ASC
        """
        params = (pattern, pattern, pattern)
    else:
        sql = """
            SELECT * FROM students
            WHERE student_id LIKE ? OR name LIKE ? OR roll_number LIKE ?
            ORDER BY name ASC
        """
        params = (pattern, pattern, pattern)

    with get_db_connection(db_path) as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]


def update_student(
    id_val: int,
    name: Optional[str] = None,
    roll_number: Optional[str] = None,
    class_name: Optional[str] = None,
    section: Optional[str] = None,
    phone: Optional[str] = None,
    status: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Optional[Dict[str, Any]]:
    """Update student fields."""
    existing = get_student_by_id(id_val, db_path=db_path)
    if not existing:
        raise ValueError(f"Student with ID {id_val} does not exist.")

    fields = []
    params = []

    if name is not None:
        name_clean = name.strip()
        if not name_clean:
            raise ValueError("Student name cannot be empty.")
        fields.append("name = ?")
        params.append(name_clean)

    if roll_number is not None:
        fields.append("roll_number = ?")
        params.append(roll_number.strip() if roll_number else None)

    if class_name is not None:
        class_clean = class_name.strip()
        if not class_clean:
            raise ValueError("Class name cannot be empty.")
        fields.append("class_name = ?")
        params.append(class_clean)

    if section is not None:
        section_clean = section.strip()
        if not section_clean:
            raise ValueError("Section cannot be empty.")
        fields.append("section = ?")
        params.append(section_clean)

    if phone is not None:
        fields.append("phone = ?")
        params.append(phone.strip() if phone else None)

    if status is not None:
        status_clean = status.strip().lower()
        if status_clean not in ("active", "inactive"):
            raise ValueError("Status must be 'active' or 'inactive'.")
        fields.append("status = ?")
        params.append(status_clean)

    if not fields:
        return existing

    fields.append("updated_at = CURRENT_TIMESTAMP")
    params.append(id_val)

    query = f"UPDATE students SET {', '.join(fields)} WHERE id = ?"

    try:
        with get_db_connection(db_path) as conn:
            conn.execute(query, params)
            row = conn.execute("SELECT * FROM students WHERE id = ?", (id_val,)).fetchone()
            return dict(row) if row else None
    except sqlite3.IntegrityError as e:
        raise ValueError(f"Update failed due to unique constraint: {e}") from e


def deactivate_student(id_val: int, db_path: Optional[Union[str, Path]] = None) -> bool:
    """Deactivate a student by setting status to 'inactive'."""
    res = update_student(id_val, status="inactive", db_path=db_path)
    return res is not None and res.get("status") == "inactive"


# ============================================================================
# USER REPOSITORY
# ============================================================================

VALID_ROLES = {"admin", "teacher"}
VALID_USER_STATUSES = {"active", "inactive"}


def create_user(
    username: str,
    password_hash: str,
    role: str = "teacher",
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Create a new system user record."""
    username = (username or "").strip()
    password_hash = (password_hash or "").strip()
    role = (role or "").strip().lower()

    if not username:
        raise ValueError("Username cannot be empty.")
    if not password_hash:
        raise ValueError("Password hash cannot be empty.")
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role '{role}'. Must be one of {VALID_ROLES}.")

    query = """
        INSERT INTO users (username, password_hash, role)
        VALUES (?, ?, ?)
    """
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (username, password_hash, role))
            new_id = cursor.lastrowid
            user = conn.execute("SELECT * FROM users WHERE id = ?", (new_id,)).fetchone()
            return dict(user)
    except sqlite3.IntegrityError as e:
        raise ValueError(f"Username '{username}' already exists.") from e


def get_user_by_username(username: str, db_path: Optional[Union[str, Path]] = None) -> Optional[Dict[str, Any]]:
    """Retrieve user by username."""
    username = (username or "").strip()
    if not username:
        return None
    query = "SELECT * FROM users WHERE username = ?"
    with get_db_connection(db_path) as conn:
        row = conn.execute(query, (username,)).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int, db_path: Optional[Union[str, Path]] = None) -> Optional[Dict[str, Any]]:
    """Retrieve user by user primary key ID."""
    query = "SELECT * FROM users WHERE id = ?"
    with get_db_connection(db_path) as conn:
        row = conn.execute(query, (user_id,)).fetchone()
        return dict(row) if row else None


def update_user_password(user_id: int, new_password_hash: str, db_path: Optional[Union[str, Path]] = None) -> bool:
    """Update password hash for a user."""
    new_password_hash = (new_password_hash or "").strip()
    if not new_password_hash:
        raise ValueError("Password hash cannot be empty.")
    
    query = "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    with get_db_connection(db_path) as conn:
        cursor = conn.execute(query, (new_password_hash, user_id))
        return cursor.rowcount > 0


def list_users(db_path: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
    """List all system users."""
    query = "SELECT id, username, role, status, created_at, updated_at FROM users ORDER BY username ASC"
    with get_db_connection(db_path) as conn:
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]


def count_users(db_path: Optional[Union[str, Path]] = None) -> int:
    """Return total count of registered users."""
    query = "SELECT COUNT(*) as cnt FROM users"
    with get_db_connection(db_path) as conn:
        row = conn.execute(query).fetchone()
        return row["cnt"] if row else 0


def update_user_status(user_id: int, status: str, db_path: Optional[Union[str, Path]] = None) -> bool:
    """Update active/inactive status for a user."""
    status_clean = (status or "").strip().lower()
    if status_clean not in VALID_USER_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of {VALID_USER_STATUSES}.")
    
    query = "UPDATE users SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    with get_db_connection(db_path) as conn:
        cursor = conn.execute(query, (status_clean, user_id))
        return cursor.rowcount > 0


# ============================================================================
# ATTENDANCE REPOSITORY
# ============================================================================

VALID_ATTENDANCE_STATUSES = {"Present", "Absent", "Late", "Excused"}


def check_duplicate_attendance(
    student_id: int,
    attendance_date: str,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    """Check if attendance record already exists for student on given date."""
    query = "SELECT 1 FROM attendance WHERE student_id = ? AND attendance_date = ?"
    with get_db_connection(db_path) as conn:
        row = conn.execute(query, (student_id, attendance_date)).fetchone()
        return row is not None


def create_attendance(
    student_id: int,
    attendance_date: str,
    attendance_time: str,
    status: str = "Present",
    recognition_method: str = "automatic",
    confidence_score: Optional[float] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Create a new attendance record."""
    status = (status or "").strip().capitalize()
    if status not in VALID_ATTENDANCE_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of {VALID_ATTENDANCE_STATUSES}.")

    # Foreign key / existence validation
    student = get_student_by_id(student_id, db_path=db_path)
    if not student:
        raise ValueError(f"Student with ID {student_id} does not exist.")

    # Duplicate check
    if check_duplicate_attendance(student_id, attendance_date, db_path=db_path):
        raise ValueError(f"Attendance already recorded for student ID {student_id} on {attendance_date}.")

    query = """
        INSERT INTO attendance (student_id, attendance_date, attendance_time, status, recognition_method, confidence_score)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                query,
                (student_id, attendance_date, attendance_time, status, recognition_method, confidence_score),
            )
            new_id = cursor.lastrowid
            row = conn.execute("SELECT * FROM attendance WHERE id = ?", (new_id,)).fetchone()
            return dict(row)
    except sqlite3.IntegrityError as e:
        raise ValueError(f"Failed to record attendance due to constraint: {e}") from e


def get_attendance_by_student(
    student_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """Retrieve all attendance records for a specific student."""
    query = "SELECT * FROM attendance WHERE student_id = ? ORDER BY attendance_date DESC, attendance_time DESC"
    with get_db_connection(db_path) as conn:
        rows = conn.execute(query, (student_id,)).fetchall()
        return [dict(row) for row in rows]


def get_attendance_by_date(
    attendance_date: str,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """Retrieve all attendance records for a specific date."""
    query = """
        SELECT a.*, s.student_id as student_code, s.name as student_name, s.class_name, s.section
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.attendance_date = ?
        ORDER BY a.attendance_time ASC
    """
    with get_db_connection(db_path) as conn:
        rows = conn.execute(query, (attendance_date,)).fetchall()
        return [dict(row) for row in rows]


def list_recent_attendance(
    limit: int = 50,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """List recent attendance records with student metadata."""
    query = """
        SELECT a.*, s.student_id as student_code, s.name as student_name, s.class_name, s.section
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        ORDER BY a.created_at DESC
        LIMIT ?
    """
    with get_db_connection(db_path) as conn:
        rows = conn.execute(query, (limit,)).fetchall()
        return [dict(row) for row in rows]


# ============================================================================
# FACE DATA REPOSITORY
# ============================================================================

def create_or_update_face_data(
    student_id: int,
    model_identifier: str,
    encoding_data: str,
    data_format: str = "json",
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Store or update face encoding/embedding data for a student."""
    model_identifier = (model_identifier or "").strip()
    encoding_data = (encoding_data or "").strip()
    data_format = (data_format or "json").strip().lower()

    if not model_identifier:
        raise ValueError("Model identifier cannot be empty.")
    if not encoding_data:
        raise ValueError("Encoding data cannot be empty.")

    student = get_student_by_id(student_id, db_path=db_path)
    if not student:
        raise ValueError(f"Student with ID {student_id} does not exist.")

    existing = get_face_data_by_student(student_id, db_path=db_path)

    with get_db_connection(db_path) as conn:
        if existing:
            query = """
                UPDATE face_data
                SET model_identifier = ?, encoding_data = ?, data_format = ?, status = 'active', updated_at = CURRENT_TIMESTAMP
                WHERE student_id = ?
            """
            conn.execute(query, (model_identifier, encoding_data, data_format, student_id))
        else:
            query = """
                INSERT INTO face_data (student_id, model_identifier, encoding_data, data_format)
                VALUES (?, ?, ?, ?)
            """
            conn.execute(query, (student_id, model_identifier, encoding_data, data_format))

        row = conn.execute("SELECT * FROM face_data WHERE student_id = ? AND status = 'active'", (student_id,)).fetchone()
        return dict(row)


def get_face_data_by_student(
    student_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> Optional[Dict[str, Any]]:
    """Retrieve active face data for a student."""
    query = "SELECT * FROM face_data WHERE student_id = ? AND status = 'active'"
    with get_db_connection(db_path) as conn:
        row = conn.execute(query, (student_id,)).fetchone()
        return dict(row) if row else None


def deactivate_face_data(
    student_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    """Deactivate face data record for a student."""
    query = "UPDATE face_data SET status = 'inactive', updated_at = CURRENT_TIMESTAMP WHERE student_id = ?"
    with get_db_connection(db_path) as conn:
        cursor = conn.execute(query, (student_id,))
        return cursor.rowcount > 0


# ============================================================================
# APPLICATION SETTINGS REPOSITORY
# ============================================================================

def get_setting(
    key: str,
    default: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Optional[str]:
    """Retrieve application setting value by key."""
    key = (key or "").strip()
    if not key:
        return default
    query = "SELECT value FROM application_settings WHERE key = ?"
    with get_db_connection(db_path) as conn:
        row = conn.execute(query, (key,)).fetchone()
        return row["value"] if row else default


def set_setting(
    key: str,
    value: str,
    description: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    """Insert or update application setting."""
    key = (key or "").strip()
    value = str(value)
    if not key:
        raise ValueError("Setting key cannot be empty.")

    query = """
        INSERT INTO application_settings (key, value, description, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET
            value = excluded.value,
            description = COALESCE(excluded.description, application_settings.description),
            updated_at = CURRENT_TIMESTAMP
    """
    with get_db_connection(db_path) as conn:
        conn.execute(query, (key, value, description))
        return True


def get_all_settings(db_path: Optional[Union[str, Path]] = None) -> Dict[str, str]:
    """Retrieve all application settings as key-value dictionary."""
    query = "SELECT key, value FROM application_settings"
    with get_db_connection(db_path) as conn:
        rows = conn.execute(query).fetchall()
        return {row["key"]: row["value"] for row in rows}
