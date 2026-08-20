"""
Student Management package for AI-Enabled Smart Attendance System.
Exposes student validation, authorization-checked CRUD workflows, and search services.
"""

from app.students.validation import validate_student_inputs
from app.students.service import (
    add_student,
    update_student_details,
    deactivate_student_record,
    get_student_detail,
    list_all_students,
    find_students,
)

from app.students.registration import (
    register_student_face,
    reregister_student_face,
    deregister_student_face,
    get_student_registration_status,
)

__all__ = [
    "validate_student_inputs",
    "add_student",
    "update_student_details",
    "deactivate_student_record",
    "get_student_detail",
    "list_all_students",
    "find_students",
    "register_student_face",
    "reregister_student_face",
    "deregister_student_face",
    "get_student_registration_status",
]
