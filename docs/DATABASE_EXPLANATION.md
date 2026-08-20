# Database Schema & Relational Structure Explanation

## 1. Overview

The AI-Enabled Smart Attendance System utilizes a lightweight, serverless SQLite 3 relational database (`data/attendance.db`).

Key features:
- **100% Local & Embedded**: Zero external database server processes required.
- **Foreign Key Constraints Enabled**: Enforces referential integrity across relational tables (`PRAGMA foreign_keys = ON;`).
- **Parameterized Queries**: All repository queries use parameterized placeholders (`?`) preventing SQL injection vulnerabilities.
- **Transaction Safety**: Data mutations execute inside atomic transaction blocks with automatic rollback on errors.

---

## 2. Relational Database Schema

```text
+-----------------------+        +-----------------------+
|       STUDENTS        |        |       ATTENDANCE      |
+-----------------------+        +-----------------------+
| id (PK, INTEGER)      |<-------| id (PK, INTEGER)      |
| student_id (UNIQUE)   |        | student_id (FK)       |
| name (TEXT)           |        | attendance_date (TEXT)|
| class_name (TEXT)     |        | attendance_time (TEXT)|
| section (TEXT)        |        | status (TEXT)         |
| roll_number (TEXT)    |        | confidence_score (REAL|
| status (TEXT)         |        | UNIQUE(student, date) |
+-----------------------+        +-----------------------+
            ^
            |
+-----------------------+        +-----------------------+
|       FACE_DATA       |        |         USERS         |
+-----------------------+        +-----------------------+
| id (PK, INTEGER)      |        | id (PK, INTEGER)      |
| student_id (FK)       |        | username (UNIQUE)     |
| model_identifier      |        | password_hash (TEXT)  |
| encoding_data (JSON)  |        | role (ADMIN/TEACHER)  |
| data_format (TEXT)    |        | status (TEXT)         |
+-----------------------+        +-----------------------+
```

---

## 3. Table Data Dictionary

### Table 1: `students`
Stores active and deactivated student profiles.
- `id` (INTEGER, Primary Key, Auto-Increment)
- `student_id` (TEXT, Unique, Not Null) — Academic Student Code (e.g. `STU-101`)
- `name` (TEXT, Not Null) — Full Name
- `class_name` (TEXT, Not Null) — Class (e.g. `12`)
- `section` (TEXT, Not Null) — Section (e.g. `A`)
- `roll_number` (TEXT) — Class Roll Number
- `guardian_phone` (TEXT) — Contact phone number
- `status` (TEXT, Default `'active'`) — Profile state (`'active'` / `'inactive'`)
- `created_at` / `updated_at` (TIMESTAMP)

### Table 2: `face_data`
Stores enrolled 128D facial feature vectors for registered students.
- `id` (INTEGER, Primary Key)
- `student_id` (INTEGER, Foreign Key referencing `students(id)`)
- `model_identifier` (TEXT, Not Null) — Model version (`'SFace'`)
- `encoding_data` (TEXT, Not Null) — Encrypted JSON array of 128 float values
- `data_format` (TEXT, Default `'json'`)
- `status` (TEXT, Default `'active'`)

### Table 3: `attendance`
Stores daily attendance logs.
- `id` (INTEGER, Primary Key)
- `student_id` (INTEGER, Foreign Key referencing `students(id)`)
- `attendance_date` (TEXT, Not Null) — Date in `YYYY-MM-DD` format
- `attendance_time` (TEXT, Not Null) — Time in `HH:MM:SS` format
- `status` (TEXT, Default `'Present'`) — Status (`'Present'`, `'Absent'`, `'Late'`, `'Excused'`)
- `confidence_score` (REAL) — Cosine similarity score ($\ge 0.363$)
- **Constraint**: `UNIQUE(student_id, attendance_date)` — Permanent protection against duplicate daily records.

### Table 4: `users`
Stores application user accounts for RBAC authentication.
- `id` (INTEGER, Primary Key)
- `username` (TEXT, Unique, Not Null) — User login name
- `password_hash` (TEXT, Not Null) — PBKDF2:SHA256 password hash
- `role` (TEXT, Not Null) — Role privilege (`'ADMIN'` / `'TEACHER'`)
- `status` (TEXT, Default `'active'`)
