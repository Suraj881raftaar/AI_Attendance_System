# Stage 8 Implementation Plan — Attendance Management & Reports System

## Objective
Build Stage 8 of the AI-Enabled Smart Attendance System: a complete Attendance Management, Analysis & Report Export System. Provide multi-criteria attendance record search and filtering (by date range, student name/ID, class, and status), manual attendance correction/override under RBAC authorization, detailed student attendance percentage summary analytics, and data export to Excel (`.xlsx` via OpenPyXL) and CSV (`.csv` via standard library).

---

## Master Requirements
From Section 3.7, 3.8 & Stage 8 of `AI_Attendance_System_Master_Requirements.md`:
1. **Attendance Record Search & Filtering**: Filter attendance records dynamically by:
   - Date range (`start_date` to `end_date`, default today or all-time)
   - Student name / student code search
   - Class and section filter
   - Attendance status (`Present`, `Absent`, `Late`, `Excused`)
2. **Student Attendance Analytics**: Compute per-student attendance summary metrics:
   - Total session days
   - Present days count
   - Absent days count
   - Late / Excused count
   - Overall attendance percentage ($\frac{\text{Present}}{\text{Total Days}} \times 100\%$)
3. **Manual Attendance Correction**: Authorized users (teachers/admins) can manually edit or correct attendance records (update status or entry time) under RBAC authorization.
4. **Data Export**:
   - **CSV Export** (`.csv` format using Python standard `csv` library): Exports filtered attendance table cleanly for spreadsheet inspection.
   - **Excel Export** (`.xlsx` format using OpenPyXL): Exports styled multi-tab Excel workbook with formatted headers, auto-adjusted column widths, and summary breakdown sheets.
5. **RBAC & Authorization**: Enforce active user session requirements (`SessionManager`) at backend service layer.

---

## Required Features

1. **Reports & Export Service Layer (`app/reports/service.py` & `app/reports/exporter.py`)**:
   - `search_attendance_records(start_date=None, end_date=None, student_query=None, class_query=None, status_filter=None, db_path=None)`: multi-criteria attendance log filtering.
   - `get_student_attendance_summary(student_id=None, start_date=None, end_date=None, db_path=None)`: per-student attendance summary analytics.
   - `export_attendance_csv(records, output_path)`: exports attendance records to CSV.
   - `export_attendance_excel(records, output_path, summary_data=None)`: exports attendance records and summary sheets to Excel (`.xlsx`).
   - `update_attendance_record(attendance_id, new_status, new_time=None, db_path=None)`: manual attendance record correction under RBAC.
2. **Attendance Reports CustomTkinter View UI (`app/ui/reports.py`)**:
   - Filter bar: Start Date, End Date, Student Search box, Class filter, Status filter.
   - Interactive attendance table displaying filtered results with inline manual edit button per row.
   - Student attendance percentage summary view.
   - Export Panel buttons: "Export to Excel (.xlsx)" and "Export to CSV (.csv)" with file path save dialogs.
3. **Integration with Main Application Layout (`app/ui/main_window.py`)**:
   - Connect "Reports & Management" tab in top-level navigation layout.
4. **Automated Test Suite (`tests/test_stage8_reports.py`)**:
   - Automated unit & integration tests for multi-criteria search, date range filtering, student attendance percentage formulas, manual correction under RBAC, CSV file output, Excel file output via OpenPyXL, and edge cases.

---

## Existing Components Reused
- `app/database/`: `get_attendance_by_date`, `get_attendance_by_student`, `list_students`, `get_student_by_id`, `get_db_connection`.
- `app/auth/`: `get_session()`, `SessionManager` (session validation and RBAC).
- `app/students/`: `list_all_students()`, `get_student_detail()`.
- `app/attendance/`: `record_manual_attendance()`.
- `app/ui/`: CustomTkinter UI framework.

---

## New Components
- **`app/reports/service.py`**: High-level Reports Service module handling multi-criteria filtering, student attendance analytics, and manual record correction under RBAC.
- **`app/reports/exporter.py`**: Data export module implementing CSV and OpenPyXL Excel spreadsheet generation.
- **`app/reports/__init__.py`**: Package initialization exposing report and export service functions.
- **`app/ui/reports.py`**: Dedicated CustomTkinter Reports & Attendance Management View component (`ReportsViewFrame`).
- **`tests/test_stage8_reports.py`**: Dedicated automated test suite for Stage 8 Reports & Export System.

---

## Database Changes
- **No Schema Changes Required**.
- Uses existing Stage 1 SQLite `students` and `attendance` tables.
- Adds helper repository function `update_attendance(attendance_id, status, time)` to `app/database/repository.py` if needed.

---

## AI Integration
- Reuses existing Stage 4 AI engine configuration and thresholds where appropriate.

---

## Authentication/RBAC
- Backend service methods (`search_attendance_records`, `update_attendance_record`, `export_attendance_csv`, `export_attendance_excel`) enforce active session checks via `_require_authenticated_user()`. Unauthenticated requests throw `PermissionError`.

---

## UI
- `ReportsViewFrame` (`app/ui/reports.py`) featuring:
  - Filter Controls Header (Date Range, Search Entry, Status Dropdown, Apply & Reset Filter)
  - Interactive Filtered Attendance Records Table with Edit Action per row
  - Individual Student Attendance Percentage Summary Panel
  - Export Controls (Export to Excel, Export to CSV)

---

## Security
- **Local Storage & Export Only**: All data exports written to user-selected local file paths.
- **Zero Remote Data Transmission**: 100% offline local processing.
- **Parameterized SQL**: All search and update queries use parameterized bindings (`?`).
- **Zero Sensitive Biometric Vector Logging**: Export files contain ONLY academic attendance metadata (Date, Time, Student Name, Student ID, Class, Status, Method). Zero face embeddings or images included.

---

## Performance
- Target System: Intel Core i3-12100 CPU, 12 GB RAM, Integrated Intel UHD 730, Windows 10.
- Filter Query Latency: < 5 ms for 1,000+ attendance records.
- Excel/CSV Export Latency: < 50 ms for typical school class sizes.
- Memory Overhead: < 2.0 MB RAM allocation.

---

## Testing
- Automated test suite in `tests/test_stage8_reports.py`:
  - RBAC authorization check
  - Multi-criteria search (by student ID/name, class, status)
  - Date range filter accuracy (`start_date` to `end_date`)
  - Student attendance percentage calculation accuracy
  - Manual attendance correction under RBAC
  - CSV file generation and header/row content verification
  - Excel `.xlsx` file generation via OpenPyXL and sheet structure verification
  - Empty search result & edge case handling

---

## Documentation
- `docs/STAGE_8_IMPLEMENTATION_PLAN.md` (this plan)
- `docs/STAGE_8_IMPLEMENTATION.md`
- `docs/STAGE_8_TESTING.md`
- `docs/STAGE_8_REPORT.md`
- `docs/REPORTS_AND_EXPORTS.md`

---

## Implementation Substages
- **5A / 8A**: Database Repository Helper & Reports Service Layer (`app/reports/service.py`, `app/reports/exporter.py`, `app/reports/__init__.py`).
- **8B**: CustomTkinter Reports View UI (`app/ui/reports.py`) with search/filter bar, attendance table, edit dialog, and export buttons.
- **8C**: UI Navigation Integration connecting Reports View with top-level main window navigation layout.
- **8D**: Comprehensive Automated Test Suite (`tests/test_stage8_reports.py`) & Documentation.

---

## Exit Criteria
- [ ] Multi-criteria search correctly filters attendance records by date range, student, class, and status.
- [ ] Student attendance percentage summary accurately calculates per-student attendance rates.
- [ ] Authorized users can manually correct/edit attendance record status or entry time under RBAC.
- [ ] Filtered attendance data exports cleanly to `.csv` format.
- [ ] Filtered attendance data exports cleanly to `.xlsx` Excel format via OpenPyXL with formatted headers and summary sheets.
- [ ] Session RBAC authorization enforced at backend service layer.
- [ ] All existing (96) and new Stage 8 tests pass (target: 105+ tests).
- [ ] Production application launches without errors (`main.py`).
- [ ] Working tree clean, zero secrets/biometric photos committed, Git checkpoint created.

---

## Risks
- **None identified**. Operates on existing SQLite database tables and standard openpyxl/csv python packages.

---

## Rollback Strategy
If any regression occurs during Stage 8 development, revert to git commit `92a2c60` (`stage-7: implement management dashboard`).
