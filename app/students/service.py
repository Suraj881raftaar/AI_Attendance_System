"""
Student Service layer for AI-Enabled Smart Attendance System.
Enforces backend RBAC authorization, input validation, and business workflows.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.database import (
    create_student,
    get_student_by_id,
    get_student_by_student_id,
    list_students,
    search_students,
    update_student,
    deactivate_student,
    get_face_data_by_student,
)
from app.auth import get_session
from app.students.validation import validate_student_inputs

logger = logging.getLogger(__name__)


def _require_authenticated_user() -> Dict[str, Any]:
    """Ensure an active user session exists, raising PermissionError if unauthorized."""
    session = get_session()
    if not session.is_logged_in():
        raise PermissionError("Authentication required to perform student operations.")
    return session.get_current_user()  # type: ignore


def add_student(
    student_id: str,
    name: str,
    class_name: str,
    section: str,
    roll_number: Optional[str] = None,
    phone: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Add a new student to the system after authorization and input validation.
    
    :raises PermissionError: If session is unauthenticated.
    :raises ValueError: If input validation fails or duplicate student ID exists.
    """
    _require_authenticated_user()

    is_valid, result = validate_student_inputs(
        student_id=student_id,
        name=name,
        class_name=class_name,
        section=section,
        roll_number=roll_number,
        phone=phone,
    )
    if not is_valid:
        error_msg = "; ".join(result.values())
        raise ValueError(error_msg)

    new_student = create_student(
        student_id=result["student_id"],
        name=result["name"],
        class_name=result["class_name"],
        section=result["section"],
        roll_number=result["roll_number"],
        phone=result["phone"],
        db_path=db_path,
    )
    logger.info(f"Student '{new_student['name']}' ({new_student['student_id']}) added successfully.")
    return new_student


def update_student_details(
    id_val: int,
    name: Optional[str] = None,
    roll_number: Optional[str] = None,
    class_name: Optional[str] = None,
    section: Optional[str] = None,
    phone: Optional[str] = None,
    status: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Update student details after authorization.
    
    :raises PermissionError: If unauthenticated.
    :raises ValueError: If student not found or duplicate constraint fails.
    """
    _require_authenticated_user()

    updated = update_student(
        id_val=id_val,
        name=name,
        roll_number=roll_number,
        class_name=class_name,
        section=section,
        phone=phone,
        status=status,
        db_path=db_path,
    )
    if not updated:
        raise ValueError(f"Student with ID {id_val} does not exist.")

    logger.info(f"Student ID {id_val} updated successfully.")
    return updated


def deactivate_student_record(
    id_val: int,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    """
    Deactivate a student record (soft deletion). Preserves historical attendance.
    
    :raises PermissionError: If unauthenticated.
    """
    _require_authenticated_user()

    success = deactivate_student(id_val, db_path=db_path)
    if success:
        logger.info(f"Student ID {id_val} marked inactive.")
    return success


def get_student_detail(
    id_val: int,
    db_path: Optional[Union[str, Path]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Retrieve comprehensive student detail including face enrollment status boundary.
    """
    _require_authenticated_user()

    student = get_student_by_id(id_val, db_path=db_path)
    if not student:
        return None

    detail = dict(student)
    # Stage 4 Preparation: Check if active face encoding data exists
    face_rec = get_face_data_by_student(id_val, db_path=db_path)
    detail["has_face_data"] = face_rec is not None
    detail["face_data_status"] = "Enrolled" if face_rec else "Pending (Stage 4)"
    return detail


def list_all_students(
    active_only: bool = True,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """Retrieve list of all students."""
    _require_authenticated_user()
    return list_students(active_only=active_only, db_path=db_path)


def find_students(
    query_str: str,
    active_only: bool = True,
    db_path: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    """Search students by Student ID, Name, or Roll Number."""
    _require_authenticated_user()
    return search_students(query_str=query_str, active_only=active_only, db_path=db_path)
