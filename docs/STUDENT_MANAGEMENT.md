# Student Management Architecture & Specification

## 1. Overview

The **Student Management Module** (`app/students/`) provides authorized student administration for the AI-Enabled Smart Attendance System. It manages student profiles, data validation, multi-criteria search, soft deactivation, and backend RBAC authorization, while preparing database boundaries for Stage 4 AI face enrollment.

---

## 2. Student Fields & Schema

Students are stored in the SQLite `students` table (`data/attendance.db`):

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | Yes | Database primary key (Auto-increment) |
| `student_id` | TEXT | Yes | Unique student code / ID (e.g., `STU-1001`) |
| `name` | TEXT | Yes | Full student name |
| `class_name` | TEXT | Yes | Class / Grade (e.g., `Class 12`) |
| `section` | TEXT | Yes | Section identifier (e.g., `A`) |
| `roll_number` | TEXT | No | Roll number (Unique if provided) |
| `phone` | TEXT | No | Contact phone number |
| `status` | TEXT | Yes | Record status (`active` / `inactive`) |
| `created_at` | TIMESTAMP | Yes | Registration timestamp |
| `updated_at` | TIMESTAMP | Yes | Last modification timestamp |

---

## 3. Validation Rules

Input validation is performed by `app/students/validation.py` before hitting database operations:
- `student_id`: Required, minimum length 2 characters, unique across the database.
- `name`: Required, minimum length 2 characters.
- `class_name`: Required, non-empty string.
- `section`: Required, non-empty string.
- `roll_number`: Optional, stripped string, unique if provided.
- `phone`: Optional, sanitized numeric string allowing `+`, `-`, and spaces.

---

## 4. Backend RBAC Authorization

All student operations enforce backend session authorization via `_require_authenticated_user()` in `app/students/service.py`:
- Unauthenticated requests trigger a `PermissionError("Authentication required...")`.
- Hidden UI elements do not serve as security boundaries; authorization is verified directly at the service layer.

---

## 5. Search & Filter Capability

Student searching is implemented in `app/database/repository.py` via `search_students()`:
- **Search Target Fields**: `student_id`, `name`, and `roll_number`.
- **Query Matching**: Case-insensitive SQL `LIKE %query%` pattern matching.
- **Status Filter**: Supports filtering by `active_only=True` (default) or retrieving all records including inactive ones.
- **Safety**: Safe parameterized SQL query execution preventing SQL injection.

---

## 6. Deactivation & Record Integrity

- **Soft Deactivation**: Deactivating a student updates `status` to `'inactive'`.
- **Historical Integrity**: Inactive records, their foreign key references, and past attendance logs are completely preserved.
- **Automatic Filtering**: Inactive students are excluded from standard active lists and future daily attendance checks.

---

## 7. Stage 4 AI Face Enrollment Boundary

Student detail objects (`get_student_detail()`) report face enrollment status without processing biometric data:
- `has_face_data`: Boolean indicator derived by checking if active records exist in `face_data`.
- `face_data_status`: `Enrolled` if face features are present, or `Pending (Stage 4)` if unassigned.
- Stage 4 will connect AI face embedding vectors directly to the stable `students.id` primary key.
