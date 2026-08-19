# Database Architecture & Specification

## 1. Overview

The **AI-Enabled Smart Attendance System** uses SQLite 3 as its embedded relational database store. The database layer is decoupled from UI components and handles persistent storage for:
- Student profile metadata
- Application users (Teachers & Administrators)
- Automatic and manual attendance records
- AI Face Recognition representations/embeddings (model-agnostic)
- System application settings

---

## 2. File Location & Storage

- **Local Path**: `data/attendance.db`
- **Path Resolution**: Resolved dynamically via `app.config.get_db_path()`.
- **Directory Auto-Creation**: `initialize_database()` automatically creates the `data/` directory if missing.
- **Testing Safety**: Automated tests run against isolated temporary databases (`:memory:` or temporary files) and never touch `data/attendance.db`.

---

## 3. Schema & Table Definitions

### 3.1 `schema_info`
Tracks applied database migration versioning.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `version` | INTEGER | PRIMARY KEY | Schema version number (Current: 1) |
| `applied_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date and time version was applied |

---

### 3.2 `students`
Stores student records and contact information.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal primary key |
| `student_id` | TEXT | UNIQUE, NOT NULL | School unique student ID / code |
| `roll_number` | TEXT | UNIQUE | Student roll number |
| `name` | TEXT | NOT NULL | Full name of student |
| `class_name` | TEXT | NOT NULL | Class / Grade |
| `section` | TEXT | NOT NULL | Section |
| `phone` | TEXT | NULL | Optional contact phone number |
| `status` | TEXT | DEFAULT 'active' | Student status (`active` / `inactive`) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Registration timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |

---

### 3.3 `users`
System user accounts for teacher and admin authorization.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | User primary key |
| `username` | TEXT | UNIQUE, NOT NULL | Account login username |
| `password_hash` | TEXT | NOT NULL | Securely hashed password (BCrypt / Argon2) |
| `role` | TEXT | DEFAULT 'teacher' | User permission role (`admin` / `teacher`) |
| `status` | TEXT | DEFAULT 'active' | Account status (`active` / `inactive`) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

---

### 3.4 `attendance`
Stores daily attendance records.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Record primary key |
| `student_id` | INTEGER | FK -> `students(id)` ON DELETE CASCADE | Foreign key referencing `students` |
| `attendance_date` | TEXT | NOT NULL | Date string (`YYYY-MM-DD`) |
| `attendance_time` | TEXT | NOT NULL | Time string (`HH:MM:SS`) |
| `status` | TEXT | DEFAULT 'Present' | Status (`Present`, `Absent`, `Late`, `Excused`) |
| `recognition_method` | TEXT | DEFAULT 'automatic' | Method (`automatic` / `manual`) |
| `confidence_score` | REAL | NULL | AI model confidence score |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

> **Constraint**: `UNIQUE(student_id, attendance_date)` ensures that a student cannot have duplicate attendance entries recorded for the same date.

---

### 3.5 `face_data`
Flexible representation for AI face embeddings/encodings.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Primary key |
| `student_id` | INTEGER | FK -> `students(id)` ON DELETE CASCADE | Foreign key referencing `students` |
| `model_identifier` | TEXT | NOT NULL | Model identifier (e.g., `opencv_haarcascade`, `facenet`) |
| `encoding_data` | TEXT | NOT NULL | Encoded vector representation (JSON string or blob) |
| `data_format` | TEXT | DEFAULT 'json' | Data format (`json`, `blob`, `numpy`) |
| `status` | TEXT | DEFAULT 'active' | Data status (`active` / `inactive`) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Update timestamp |

---

### 3.6 `application_settings`
Key-value application configuration store.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `key` | TEXT | PRIMARY KEY | Setting key identifier |
| `value` | TEXT | NOT NULL | Setting value string |
| `description` | TEXT | NULL | Human-readable setting description |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |

---

## 4. Foreign Key Constraints

Foreign key enforcement is enabled programmatically on every connection:
```sql
PRAGMA foreign_keys = ON;
```

---

## 5. Repository Layer Architecture

Data access operations are contained within `app/database/repository.py`:
- **Students**: `create_student`, `get_student_by_id`, `get_student_by_student_id`, `list_students`, `update_student`, `deactivate_student`
- **Users**: `create_user`, `get_user_by_username`, `update_user_status`
- **Attendance**: `create_attendance`, `check_duplicate_attendance`, `get_attendance_by_student`, `get_attendance_by_date`, `list_recent_attendance`
- **Face Data**: `create_or_update_face_data`, `get_face_data_by_student`, `deactivate_face_data`
- **Settings**: `get_setting`, `set_setting`, `get_all_settings`

---

## 6. Migration Strategy

Future schema changes are managed via `schema_info` table checks:
1. `initialize_database()` reads `CURRENT_SCHEMA_VERSION`.
2. Incremental SQL migration scripts are executed in version order.
3. Tables and columns are added using non-destructive `ALTER TABLE` operations.

---

## 7. Security & Privacy Considerations

- **No Plaintext Passwords**: Passwords are saved as hashes (`password_hash` column).
- **Parameterized SQL**: All SQL statements use `?` placeholders to prevent SQL injection.
- **Local Biometric Storage**: Face representations are stored locally in SQLite (`face_data`) and never transmitted externally.
