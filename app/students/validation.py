"""
Input validation utilities for Student Management module.
Ensures data integrity and friendly error messages prior to database entry.
"""

from typing import Dict, Any, Optional, Tuple


def validate_student_inputs(
    student_id: str,
    name: str,
    class_name: str,
    section: str,
    roll_number: Optional[str] = None,
    phone: Optional[str] = None,
) -> Tuple[bool, Dict[str, str]]:
    """
    Validate student form input fields.
    
    :return: Tuple of (is_valid: bool, cleaned_data_or_errors: Dict)
    """
    errors = {}
    cleaned = {}

    student_id_clean = (student_id or "").strip()
    name_clean = (name or "").strip()
    class_clean = (class_name or "").strip()
    section_clean = (section or "").strip()
    roll_clean = roll_number.strip() if roll_number and str(roll_number).strip() else None
    phone_clean = phone.strip() if phone and str(phone).strip() else None

    if not student_id_clean:
        errors["student_id"] = "Student ID cannot be empty."
    elif len(student_id_clean) < 2:
        errors["student_id"] = "Student ID must be at least 2 characters long."

    if not name_clean:
        errors["name"] = "Student name cannot be empty."
    elif len(name_clean) < 2:
        errors["name"] = "Student name must be at least 2 characters long."

    if not class_clean:
        errors["class_name"] = "Class name cannot be empty."

    if not section_clean:
        errors["section"] = "Section cannot be empty."

    if phone_clean and not phone_clean.replace("+", "").replace("-", "").replace(" ", "").isdigit():
        errors["phone"] = "Phone number contains invalid characters."

    if errors:
        return False, errors

    cleaned = {
        "student_id": student_id_clean,
        "name": name_clean,
        "class_name": class_clean,
        "section": section_clean,
        "roll_number": roll_clean,
        "phone": phone_clean,
    }
    return True, cleaned
