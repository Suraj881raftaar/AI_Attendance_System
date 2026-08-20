"""
Stage 1 database foundation test suite.
Verifies SQLite schema creation, foreign key enforcement, repository CRUD functions,
validation rules, duplicate constraints, and idempotency using an isolated temporary database.
"""

import pytest
from pathlib import Path

from app.database import (
    initialize_database,
    get_connection,
    # Students
    create_student,
    get_student_by_id,
    get_student_by_student_id,
    update_student,
    deactivate_student,
    # Users
    create_user,
    get_user_by_username,
    # Attendance
    create_attendance,
    check_duplicate_attendance,
    get_attendance_by_student,
    # Face Data
    create_or_update_face_data,
    get_face_data_by_student,
    deactivate_face_data,
    # Settings
    get_setting,
    set_setting,
    get_all_settings,
)


@pytest.fixture
def test_db_path(tmp_path: Path) -> Path:
    """Fixture providing a temporary SQLite database file path."""
    db_file = tmp_path / "test_attendance.db"
    initialize_database(db_file)
    return db_file


# 1. Database initializes successfully
def test_database_initialization(test_db_path: Path):
    assert test_db_path.exists()
    assert test_db_path.stat().st_size > 0


# 2. Required tables exist
def test_tables_exist(test_db_path: Path):
    expected_tables = {
        "schema_info",
        "students",
        "users",
        "attendance",
        "face_data",
        "application_settings",
    }
    with get_connection(test_db_path) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        existing_tables = {row["name"] for row in rows}
    assert expected_tables.issubset(existing_tables)


# 3. Foreign keys are enabled
def test_foreign_keys_enabled(test_db_path: Path):
    with get_connection(test_db_path) as conn:
        fk_status = conn.execute("PRAGMA foreign_keys").fetchone()[0]
    assert fk_status == 1


# 4. Database initialization is idempotent
def test_initialization_idempotency(test_db_path: Path):
    # Initialize second time on existing db
    result = initialize_database(test_db_path)
    assert result is True


# 5. Student can be created
def test_create_student(test_db_path: Path):
    student = create_student(
        student_id="STU-1001",
        name="Alice Smith",
        class_name="Class 12",
        section="A",
        roll_number="1201",
        phone="9876543210",
        db_path=test_db_path,
    )
    assert student["id"] is not None
    assert student["student_id"] == "STU-1001"
    assert student["name"] == "Alice Smith"
    assert student["status"] == "active"


# 6. Student can be retrieved by ID and student_id
def test_retrieve_student(test_db_path: Path):
    created = create_student(
        student_id="STU-1002",
        name="Bob Jones",
        class_name="Class 12",
        section="B",
        db_path=test_db_path,
    )
    by_id = get_student_by_id(created["id"], db_path=test_db_path)
    by_code = get_student_by_student_id("STU-1002", db_path=test_db_path)

    assert by_id is not None
    assert by_code is not None
    assert by_id["name"] == "Bob Jones"
    assert by_code["id"] == created["id"]


# 7. Student can be updated
def test_update_student(test_db_path: Path):
    student = create_student(
        student_id="STU-1003",
        name="Charlie Brown",
        class_name="Class 11",
        section="A",
        db_path=test_db_path,
    )
    updated = update_student(
        student["id"],
        name="Charlie Vance",
        class_name="Class 12",
        db_path=test_db_path,
    )
    assert updated["name"] == "Charlie Vance"
    assert updated["class_name"] == "Class 12"


# 8. Student can be deactivated
def test_deactivate_student(test_db_path: Path):
    student = create_student(
        student_id="STU-1004",
        name="David Miller",
        class_name="Class 10",
        section="C",
        db_path=test_db_path,
    )
    success = deactivate_student(student["id"], db_path=test_db_path)
    assert success is True
    retrieved = get_student_by_id(student["id"], db_path=test_db_path)
    assert retrieved["status"] == "inactive"


# 9. Duplicate student ID is rejected
def test_duplicate_student_id_rejected(test_db_path: Path):
    create_student(
        student_id="STU-1005",
        name="Eve Adams",
        class_name="Class 12",
        section="A",
        db_path=test_db_path,
    )
    with pytest.raises(ValueError, match="already exists"):
        create_student(
            student_id="STU-1005",
            name="Eve Duplicate",
            class_name="Class 12",
            section="A",
            db_path=test_db_path,
        )


# 10. User can be created
def test_create_user(test_db_path: Path):
    user = create_user(
        username="teacher1",
        password_hash="$2b$12$hashedpasswordplaceholder",
        role="teacher",
        db_path=test_db_path,
    )
    assert user["id"] is not None
    assert user["username"] == "teacher1"
    assert user["role"] == "teacher"


# 11. User can be retrieved
def test_retrieve_user(test_db_path: Path):
    create_user(
        username="admin1",
        password_hash="$2b$12$adminhashplaceholder",
        role="admin",
        db_path=test_db_path,
    )
    user = get_user_by_username("admin1", db_path=test_db_path)
    assert user is not None
    assert user["role"] == "admin"


# 12. Attendance can be created
def test_create_attendance(test_db_path: Path):
    student = create_student(
        student_id="STU-2001",
        name="Frank Wright",
        class_name="Class 12",
        section="A",
        db_path=test_db_path,
    )
    attendance = create_attendance(
        student_id=student["id"],
        attendance_date="2026-08-19",
        attendance_time="08:30:00",
        status="Present",
        recognition_method="automatic",
        confidence_score=0.92,
        db_path=test_db_path,
    )
    assert attendance["id"] is not None
    assert attendance["student_id"] == student["id"]
    assert attendance["status"] == "Present"


# 13. Attendance references a valid student
def test_attendance_references_valid_student(test_db_path: Path):
    student = create_student(
        student_id="STU-2002",
        name="Grace Hopper",
        class_name="Class 12",
        section="B",
        db_path=test_db_path,
    )
    att_list = get_attendance_by_student(student["id"], db_path=test_db_path)
    assert len(att_list) == 0

    create_attendance(
        student_id=student["id"],
        attendance_date="2026-08-19",
        attendance_time="08:31:00",
        db_path=test_db_path,
    )
    att_list = get_attendance_by_student(student["id"], db_path=test_db_path)
    assert len(att_list) == 1
    assert att_list[0]["student_id"] == student["id"]


# 14. Invalid student attendance is rejected
def test_invalid_student_attendance_rejected(test_db_path: Path):
    non_existent_student_id = 99999
    with pytest.raises(ValueError, match="does not exist"):
        create_attendance(
            student_id=non_existent_student_id,
            attendance_date="2026-08-19",
            attendance_time="08:30:00",
            db_path=test_db_path,
        )


# 15. Duplicate attendance behavior works as designed
def test_duplicate_attendance_rejected(test_db_path: Path):
    student = create_student(
        student_id="STU-2003",
        name="Hank Pym",
        class_name="Class 12",
        section="A",
        db_path=test_db_path,
    )
    create_attendance(
        student_id=student["id"],
        attendance_date="2026-08-19",
        attendance_time="08:30:00",
        db_path=test_db_path,
    )
    assert check_duplicate_attendance(student["id"], "2026-08-19", db_path=test_db_path) is True

    with pytest.raises(ValueError, match="already recorded"):
        create_attendance(
            student_id=student["id"],
            attendance_date="2026-08-19",
            attendance_time="09:00:00",
            db_path=test_db_path,
        )


# 16. Face data can be associated with a student
def test_create_face_data(test_db_path: Path):
    student = create_student(
        student_id="STU-3001",
        name="Iris West",
        class_name="Class 12",
        section="B",
        db_path=test_db_path,
    )
    face_rec = create_or_update_face_data(
        student_id=student["id"],
        model_identifier="opencv_haarcascade_v1",
        encoding_data="[0.12, 0.45, -0.89, 0.33]",
        data_format="json",
        db_path=test_db_path,
    )
    assert face_rec["id"] is not None
    assert face_rec["student_id"] == student["id"]
    assert face_rec["model_identifier"] == "opencv_haarcascade_v1"


# 17. Face data can be updated and deactivated
def test_update_and_deactivate_face_data(test_db_path: Path):
    student = create_student(
        student_id="STU-3002",
        name="Jack Reacher",
        class_name="Class 12",
        section="C",
        db_path=test_db_path,
    )
    # Create initial
    create_or_update_face_data(
        student_id=student["id"],
        model_identifier="model_v1",
        encoding_data="data_v1",
        db_path=test_db_path,
    )
    # Update to model_v2
    updated = create_or_update_face_data(
        student_id=student["id"],
        model_identifier="model_v2",
        encoding_data="data_v2",
        db_path=test_db_path,
    )
    assert updated["model_identifier"] == "model_v2"

    # Deactivate
    deactivated = deactivate_face_data(student["id"], db_path=test_db_path)
    assert deactivated is True
    assert get_face_data_by_student(student["id"], db_path=test_db_path) is None


# 18. Settings can be stored and retrieved
def test_application_settings(test_db_path: Path):
    assert get_setting("school_name", db_path=test_db_path) == "AI Smart Academy"

    set_setting("school_name", "St. Jude High School", db_path=test_db_path)
    assert get_setting("school_name", db_path=test_db_path) == "St. Jude High School"

    set_setting("new_custom_key", "custom_value", "Test key", db_path=test_db_path)
    assert get_setting("new_custom_key", db_path=test_db_path) == "custom_value"

    all_settings = get_all_settings(test_db_path)
    assert "school_name" in all_settings
    assert "new_custom_key" in all_settings


# 19. Database survives repeated initialization
def test_db_survives_reinitialization(test_db_path: Path):
    student = create_student(
        student_id="STU-4001",
        name="Karen Page",
        class_name="Class 12",
        section="A",
        db_path=test_db_path,
    )
    # Re-run initialization
    assert initialize_database(test_db_path) is True

    retrieved = get_student_by_id(student["id"], db_path=test_db_path)
    assert retrieved is not None
    assert retrieved["name"] == "Karen Page"


# 20. Existing data is not destroyed by initialization
def test_data_not_destroyed_by_init(test_db_path: Path):
    student = create_student(
        student_id="STU-5001",
        name="Leo Fitz",
        class_name="Class 12",
        section="A",
        db_path=test_db_path,
    )
    create_attendance(
        student_id=student["id"],
        attendance_date="2026-08-19",
        attendance_time="08:00:00",
        db_path=test_db_path,
    )
    set_setting("school_name", "Shield Academy", db_path=test_db_path)

    # Re-initialize
    initialize_database(test_db_path)

    # Verify student, attendance, and setting persist
    assert get_student_by_student_id("STU-5001", db_path=test_db_path) is not None
    assert len(get_attendance_by_student(student["id"], db_path=test_db_path)) == 1
    assert get_setting("school_name", db_path=test_db_path) == "Shield Academy"
