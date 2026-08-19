"""
Stage 3 student management test suite.
Verifies student validation, authorization service checks, CRUD operations,
soft deactivation, multi-criteria search, and Stage 4 face data relation preparation using temporary databases.
"""

import pytest
from pathlib import Path

from app.database import (
    initialize_database,
    create_user,
    create_or_update_face_data,
    get_connection,
)
from app.auth import get_session, hash_password
from app.students import (
    validate_student_inputs,
    add_student,
    update_student_details,
    deactivate_student_record,
    get_student_detail,
    list_all_students,
    find_students,
)


@pytest.fixture
def student_db_path(tmp_path: Path) -> Path:
    """Fixture providing temporary test database with authenticated test user session."""
    db_file = tmp_path / "test_students.db"
    initialize_database(db_file)
    session = get_session()
    session.clear_session()
    
    # Create and login test user
    pw_hash = hash_password("TeacherPass123")
    user = create_user("test_teacher", pw_hash, role="teacher", db_path=db_file)
    session.start_session(user)
    
    yield db_file
    session.clear_session()


# 1. Student creation works
def test_student_creation(student_db_path: Path):
    student = add_student(
        student_id="STU-3001",
        name="Alexander Hamilton",
        class_name="Class 12",
        section="A",
        roll_number="1201",
        phone="9876543210",
        db_path=student_db_path,
    )
    assert student["id"] is not None
    assert student["student_id"] == "STU-3001"
    assert student["name"] == "Alexander Hamilton"
    assert student["status"] == "active"


# 2. Required-field validation works
def test_student_field_validation():
    is_valid, errors = validate_student_inputs(
        student_id="",
        name="",
        class_name="",
        section="",
    )
    assert is_valid is False
    assert "student_id" in errors
    assert "name" in errors
    assert "class_name" in errors
    assert "section" in errors

    valid_res, cleaned = validate_student_inputs(
        student_id="STU-3002",
        name="Benjamin Franklin",
        class_name="Class 11",
        section="B",
    )
    assert valid_res is True
    assert cleaned["student_id"] == "STU-3002"


# 3. Duplicate Student ID rejection
def test_duplicate_student_id_rejected(student_db_path: Path):
    add_student(
        student_id="STU-3003",
        name="Clara Barton",
        class_name="Class 12",
        section="A",
        db_path=student_db_path,
    )
    with pytest.raises(ValueError, match="already exists"):
        add_student(
            student_id="STU-3003",
            name="Clara Duplicate",
            class_name="Class 12",
            section="A",
            db_path=student_db_path,
        )


# 4. Student retrieval works
def test_student_retrieval(student_db_path: Path):
    created = add_student(
        student_id="STU-3004",
        name="Daniel Webster",
        class_name="Class 10",
        section="C",
        db_path=student_db_path,
    )
    detail = get_student_detail(created["id"], db_path=student_db_path)
    assert detail is not None
    assert detail["name"] == "Daniel Webster"
    assert detail["has_face_data"] is False
    assert detail["face_data_status"] == "Pending (Stage 4)"


# 5. Student update works
def test_student_update(student_db_path: Path):
    created = add_student(
        student_id="STU-3005",
        name="Eleanor Roosevelt",
        class_name="Class 11",
        section="A",
        db_path=student_db_path,
    )
    updated = update_student_details(
        created["id"],
        name="Eleanor R. Vance",
        class_name="Class 12",
        section="B",
        db_path=student_db_path,
    )
    assert updated["name"] == "Eleanor R. Vance"
    assert updated["class_name"] == "Class 12"
    assert updated["section"] == "B"


# 6 & 7. Student deactivation works & inactive record remains in DB
def test_student_deactivation_persistence(student_db_path: Path):
    created = add_student(
        student_id="STU-3006",
        name="Florence Nightingale",
        class_name="Class 12",
        section="A",
        db_path=student_db_path,
    )
    success = deactivate_student_record(created["id"], db_path=student_db_path)
    assert success is True

    # Detail view still retrieves record with inactive status
    detail = get_student_detail(created["id"], db_path=student_db_path)
    assert detail is not None
    assert detail["status"] == "inactive"

    # Listed active students excludes inactive by default
    active_list = list_all_students(active_only=True, db_path=student_db_path)
    active_ids = [s["id"] for s in active_list]
    assert created["id"] not in active_ids


# 8. Search by Student ID
def test_search_by_student_id(student_db_path: Path):
    add_student(
        student_id="STU-3007",
        name="George Washington",
        class_name="Class 12",
        section="A",
        db_path=student_db_path,
    )
    results = find_students("STU-3007", db_path=student_db_path)
    assert len(results) == 1
    assert results[0]["name"] == "George Washington"


# 9 & 11. Search by name & partial-name search
def test_search_by_name_and_partial(student_db_path: Path):
    add_student(
        student_id="STU-3008",
        name="Harriet Tubman",
        class_name="Class 12",
        section="B",
        db_path=student_db_path,
    )
    # Full name search
    res1 = find_students("Harriet Tubman", db_path=student_db_path)
    assert len(res1) == 1

    # Partial case-insensitive search
    res2 = find_students("tubman", db_path=student_db_path)
    assert len(res2) == 1
    assert res2[0]["student_id"] == "STU-3008"


# 10. Search by roll number
def test_search_by_roll_number(student_db_path: Path):
    add_student(
        student_id="STU-3009",
        name="Isaac Newton",
        class_name="Class 12",
        section="A",
        roll_number="ROLL-99",
        db_path=student_db_path,
    )
    results = find_students("ROLL-99", db_path=student_db_path)
    assert len(results) == 1
    assert results[0]["name"] == "Isaac Newton"


# 12. No-result search behavior
def test_search_no_results(student_db_path: Path):
    add_student(
        student_id="STU-3010",
        name="John Locke",
        class_name="Class 12",
        section="A",
        db_path=student_db_path,
    )
    results = find_students("NONEXISTENT_QUERY_123", db_path=student_db_path)
    assert len(results) == 0


# 13, 14, 15. Unauthorized operations raise PermissionError
def test_unauthorized_student_operations(tmp_path: Path):
    db_file = tmp_path / "test_unauth.db"
    initialize_database(db_file)
    get_session().clear_session()  # Clear active user session

    with pytest.raises(PermissionError, match="Authentication required"):
        add_student("STU-9999", "Unauth User", "Class 10", "A", db_path=db_file)

    with pytest.raises(PermissionError, match="Authentication required"):
        update_student_details(1, name="New Name", db_path=db_file)

    with pytest.raises(PermissionError, match="Authentication required"):
        deactivate_student_record(1, db_path=db_file)

    with pytest.raises(PermissionError, match="Authentication required"):
        list_all_students(db_path=db_file)

    with pytest.raises(PermissionError, match="Authentication required"):
        find_students("test", db_path=db_file)


# 16. Authorized operations work cleanly
def test_authorized_operations(student_db_path: Path):
    # Logged in via fixture
    stu = add_student("STU-3011", "Kathrine Johnson", "Class 12", "A", db_path=student_db_path)
    assert stu["id"] is not None
    assert list_all_students(db_path=student_db_path) is not None


# 17 & 18. Student identity stability and future face_data relationship
def test_face_data_relationship_preparation(student_db_path: Path):
    student = add_student(
        student_id="STU-3012",
        name="Ada Lovelace",
        class_name="Class 12",
        section="A",
        db_path=student_db_path,
    )

    # Attach face data mock to student.id foreign key
    face_rec = create_or_update_face_data(
        student_id=student["id"],
        model_identifier="stage4_prep_model",
        encoding_data="[0.1, 0.2, 0.3]",
        db_path=student_db_path,
    )
    assert face_rec["student_id"] == student["id"]

    # Student detail boundary now reflects active face data
    detail = get_student_detail(student["id"], db_path=student_db_path)
    assert detail["has_face_data"] is True
    assert detail["face_data_status"] == "Enrolled"


# 19. Database integrity remains intact
def test_database_foreign_key_integrity(student_db_path: Path):
    with get_connection(student_db_path) as conn:
        fk_status = conn.execute("PRAGMA foreign_keys").fetchone()[0]
    assert fk_status == 1
