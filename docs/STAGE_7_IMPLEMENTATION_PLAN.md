# Stage 7 Implementation Plan — Management Dashboard System

## Objective
Build Stage 7 of the AI-Enabled Smart Attendance System: a central Management Dashboard view and service layer. Present live summary statistics cards (Total Registered Students, Present Today, Absent Today, Attendance Percentage), a recent attendance activity log table, quick navigation action buttons, and automatic/manual refresh functionality matching the local SQLite database.

---

## Master Requirements
From Section 3.6 & Stage 7 of `AI_Attendance_System_Master_Requirements.md`:
1. **Summary Statistics Cards**: Display accurate real-time metrics for:
   - `TOTAL STUDENTS`: Count of active registered students in SQLite.
   - `PRESENT TODAY`: Count of unique students marked Present for today's date (`YYYY-MM-DD`).
   - `ABSENT TODAY`: Count of active students not yet marked Present today (`Total - Present`).
   - `ATTENDANCE %`: Today's overall attendance rate ($\frac{\text{Present}}{\text{Total}} \times 100\%$).
2. **Recent Attendance Activity Table**: Display recent attendance records (top 10 latest) showing student name, ID, class, time, and status.
3. **Quick Navigation Action Buttons**: Provide buttons for fast user navigation:
   - "Start Attendance Camera" (launches AI Attendance Recognition view)
   - "Add New Student" (launches Student Registration view)
   - "Refresh Dashboard" (manually re-queries database and updates statistics cards & tables)
4. **Auto-Refresh Mechanism**: Dashboard automatically updates statistics upon view loading or activation.
5. **RBAC & Authorization**: Require an active user session (`SessionManager`) at backend service layer.

---

## Required Features

1. **Dashboard Service Layer (`app/dashboard/service.py`)**:
   - `get_dashboard_metrics(db_path=None)`: queries total active students, present count today, absent count today, attendance percentage, and recent attendance entries. Enforces RBAC authorization.
2. **Dashboard CustomTkinter View (`app/ui/dashboard.py`)**:
   - Modern CustomTkinter layout with prominent summary stat cards, recent activity table, quick action buttons, and refresh controls.
3. **Integration with Main Navigation Layout**:
   - Sets Dashboard as the primary landing view after user login.
4. **Automated Test Suite (`tests/test_stage7_dashboard.py`)**:
   - Unit and integration tests for dashboard service calculations, database consistency, zero-student edge cases, recent attendance query ordering, and RBAC authorization.

---

## Existing Components Reused
- `app/database/`: `list_students`, `get_attendance_by_date`, `list_recent_attendance`, `get_student_by_id`.
- `app/auth/`: `get_session()`, `SessionManager` (session validation and RBAC).
- `app/students/`: `list_all_students()`, `get_student_detail()`.
- `app/attendance/`: `get_today_attendance_summary()`.
- `app/ui/`: CustomTkinter UI framework.

---

## New Components
- **`app/dashboard/service.py`**: High-level Dashboard Service module computing summary metrics and recent activity lists under RBAC authorization.
- **`app/dashboard/__init__.py`**: Package initialization exposing dashboard service functions.
- **`app/ui/dashboard.py`**: Dedicated CustomTkinter Dashboard View component (`DashboardViewFrame`).
- **`tests/test_stage7_dashboard.py`**: Dedicated automated test suite for Stage 7 Dashboard.

---

## Database Changes
- **No Schema Changes Required**.
- Uses existing Stage 1 SQLite `students` and `attendance` tables:
  ```sql
  -- Reads active students count from students table
  -- Reads today's attendance records from attendance table
  ```

---

## AI Integration
- Reuses existing Stage 4 AI engine status checks (`get_ai_runtime_status()`) to display AI model operational state on dashboard header.

---

## Authentication/RBAC
- Backend service methods (`get_dashboard_metrics`) enforce active session checks via `_require_authenticated_user()`. Unauthenticated requests throw `PermissionError`.

---

## UI
- `DashboardViewFrame` (`app/ui/dashboard.py`) featuring:
  - Header with system banner & AI status badge
  - 4 Stat Cards Grid (Total Students, Present Today, Absent Today, Attendance %)
  - Recent Attendance Table with columns (Student Name, Student ID, Class-Section, Time, Status)
  - Quick Action Buttons panel (Start Camera, Add Student, Refresh)

---

## Security
- **Local Storage Only**: Reads directly from local SQLite database (`data/attendance.db`).
- **Zero External Calls**: 100% offline local processing.
- **Parameterized Queries**: All underlying database calls use parameterized bindings.

---

## Performance
- Target System: Intel Core i3-12100 CPU, 12 GB RAM, Integrated Intel UHD 730, Windows 10.
- Dashboard Query Latency: < 5 ms for metric aggregation and table population.
- Memory Overhead: < 1.0 MB RAM allocation.

---

## Testing
- Automated test suite in `tests/test_stage7_dashboard.py`:
  - RBAC authorization check
  - Total active student count accuracy
  - Today's present count accuracy
  - Today's absent count calculation (`Total - Present`)
  - Attendance percentage calculation (with 0-student division safety)
  - Recent attendance list query ordering
  - Manual & automatic refresh consistency
  - Integration with existing database repository functions

---

## Documentation
- `docs/STAGE_7_IMPLEMENTATION_PLAN.md` (this plan)
- `docs/STAGE_7_IMPLEMENTATION.md`
- `docs/STAGE_7_TESTING.md`
- `docs/STAGE_7_REPORT.md`

---

## Implementation Substages
- **7A**: Dashboard Service Layer (`app/dashboard/service.py` & `app/dashboard/__init__.py`) connecting database repositories with RBAC.
- **7B**: CustomTkinter Dashboard View UI (`app/ui/dashboard.py`) with stat cards, recent activity table, and quick navigation buttons.
- **7C**: UI Navigation Integration connecting Dashboard with Student Management and AI Attendance engine views.
- **7D**: Comprehensive Automated Test Suite (`tests/test_stage7_dashboard.py`) & Documentation.

---

## Exit Criteria
- [ ] Dashboard displays accurate Total Students count matching SQLite database.
- [ ] Dashboard displays accurate Present Today count for current date (`YYYY-MM-DD`).
- [ ] Dashboard displays accurate Absent Today count (`Total - Present`).
- [ ] Dashboard displays accurate Attendance Percentage with 0-student safety.
- [ ] Recent Attendance Activity Table renders latest attendance logs.
- [ ] Quick Action buttons navigate smoothly between views.
- [ ] Refresh button updates statistics cards and table cleanly.
- [ ] Session RBAC authorization enforced at backend service layer.
- [ ] All existing (91) and new Stage 7 tests pass (target: 100+ tests).
- [ ] Production application launches without errors (`main.py`).
- [ ] Working tree clean, zero secrets/biometric photos committed, Git checkpoint created.

---

## Risks
- **None identified**. Operates on existing SQLite database tables and repositories.

---

## Rollback Strategy
If any regression occurs during Stage 7 development, revert to git commit `5f09550` (`test: add mobile camera input adapter`).
