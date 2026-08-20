"""
Student Face Registration Service Layer for AI-Enabled Smart Attendance System.
Handles RBAC backend authorization, transactional re-enrollment, face data de-registration,
and integration between Student Management and AI Face Enrollment Manager.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import numpy as np

from app.auth import get_session
from app.database import (
    get_student_by_id,
    get_face_data_by_student,
    create_or_update_face_data,
    deactivate_face_data,
)
from app.ai.enrollment import FaceEnrollmentManager

logger = logging.getLogger(__name__)


def _require_authenticated_user() -> Dict[str, Any]:
    """Ensure an active user session exists, raising PermissionError if unauthenticated."""
    session = get_session()
    if not session.is_logged_in():
        raise PermissionError("Authentication required to perform student face registration operations.")
    return session.get_current_user()  # type: ignore


def register_student_face(
    student_id: int,
    frames: List[np.ndarray],
    enrollment_manager: Optional[FaceEnrollmentManager] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Register a student's face embeddings from a list of valid sample frames.
    
    :param student_id: Primary key ID of target student.
    :param frames: List of BGR numpy image frame samples.
    :param enrollment_manager: Optional custom FaceEnrollmentManager instance.
    :param db_path: Optional SQLite database path override.
    :return: Result dict containing student identity and enrollment metadata.
    :raises PermissionError: If unauthenticated.
    :raises ValueError: If student inactive/not found or quality checks fail.
    """
    _require_authenticated_user()

    student = get_student_by_id(student_id, db_path=db_path)
    if not student:
        raise ValueError(f"Student with ID {student_id} does not exist.")
    if student.get("status") != "active":
        raise ValueError(f"Cannot register face data for inactive student '{student['name']}' (ID {student_id}).")

    manager = enrollment_manager or FaceEnrollmentManager(db_path=db_path)
    return manager.enroll_student_from_frames(student_id=student_id, frames=frames, db_path=db_path)


def reregister_student_face(
    student_id: int,
    frames: List[np.ndarray],
    enrollment_manager: Optional[FaceEnrollmentManager] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Re-enroll a student's face embeddings, safely replacing existing face data.
    
    TRANSACTIONAL SAFETY: If new sample validation or feature extraction fails,
    the existing active face enrollment record IS PRESERVED UNTOUCHED.
    
    :param student_id: Primary key ID of target student.
    :param frames: List of new BGR numpy image frame samples.
    :param enrollment_manager: Optional custom FaceEnrollmentManager instance.
    :param db_path: Optional SQLite database path override.
    :return: Result dict containing student identity and enrollment metadata.
    :raises PermissionError: If unauthenticated.
    :raises ValueError: If new sample validation fails (old enrollment preserved).
    """
    _require_authenticated_user()

    # 1. Verify student state
    student = get_student_by_id(student_id, db_path=db_path)
    if not student:
        raise ValueError(f"Student with ID {student_id} does not exist.")
    if student.get("status") != "active":
        raise ValueError(f"Cannot re-register face data for inactive student '{student['name']}' (ID {student_id}).")

    # 2. Check if previous face data exists
    old_face_data = get_face_data_by_student(student_id, db_path=db_path)

    manager = enrollment_manager or FaceEnrollmentManager(db_path=db_path)

    # 3. Attempt enrollment with new frames BEFORE modifying or deactivating old record
    try:
        new_result = manager.enroll_student_from_frames(student_id=student_id, frames=frames, db_path=db_path)
        logger.info(f"Re-enrollment successful for student ID {student_id}. Previous record updated cleanly.")
        return new_result
    except Exception as e:
        logger.warning(f"Re-enrollment failed for student ID {student_id}: {e}. Existing face data preserved.")
        raise ValueError(f"Re-enrollment failed: {e}. Existing face registration was preserved.") from e


def deregister_student_face(
    student_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    """
    Deactivate a student's face registration record (soft deactivation).
    Preserves historical attendance data intact.
    
    :param student_id: Primary key ID of target student.
    :param db_path: Optional SQLite database path override.
    :return: True if face data was deactivated.
    :raises PermissionError: If unauthenticated.
    """
    _require_authenticated_user()

    student = get_student_by_id(student_id, db_path=db_path)
    if not student:
        raise ValueError(f"Student with ID {student_id} does not exist.")

    success = deactivate_face_data(student_id, db_path=db_path)
    if success:
        logger.info(f"De-registered face data for student '{student['name']}' (ID {student_id}).")
    return success


def get_student_registration_status(
    student_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Query registration status and metadata for a student.
    
    :param student_id: Primary key ID of target student.
    :param db_path: Optional SQLite database path override.
    :return: Dict containing status details ('is_enrolled', 'status_label', 'face_data').
    """
    _require_authenticated_user()

    student = get_student_by_id(student_id, db_path=db_path)
    if not student:
        raise ValueError(f"Student with ID {student_id} does not exist.")

    face_rec = get_face_data_by_student(student_id, db_path=db_path)
    is_enrolled = face_rec is not None and face_rec.get("status") == "active"

    return {
        "student_id": student_id,
        "student_code": student["student_id"],
        "student_name": student["name"],
        "is_enrolled": is_enrolled,
        "status_label": "Enrolled" if is_enrolled else "Pending",
        "model_identifier": face_rec.get("model_identifier") if face_rec else None,
        "updated_at": face_rec.get("updated_at") if face_rec else None,
    }
