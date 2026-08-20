# Stage 9 Implementation Plan — Charts & Visual Analytics System

## Objective
Build Stage 9 of the AI-Enabled Smart Attendance System: a complete Charts & Visual Analytics System. Add lightweight, CPU-first graphical chart rendering displaying real attendance data from the local SQLite database. Provide daily attendance trend bar/line charts, Present vs Absent distribution donut/pie charts, monthly attendance trend charts, and student performance distribution charts.

---

## Master Requirements
From Section 3.8 & Stage 9 of `AI_Attendance_System_Master_Requirements.md`:
1. **Visual Analytics Goal**: Provide clear visual insights into school attendance patterns.
2. **Required Charts**:
   - **Daily Attendance Trend**: Tracks daily Present vs Absent student counts over a configurable date window (e.g. past 7, 14, or 30 days).
   - **Present vs Absent Distribution**: Displays proportional breakdown of Present, Absent, Late, and Excused statuses for a selected date.
   - **Monthly Attendance Trend**: Visualizes average monthly attendance percentage rates.
   - **Student Performance Distribution**: Groups active students into attendance rate bands (e.g. Excellent >90%, Good 75-90%, At-Risk <75%).
3. **Real Database Data**: All charts MUST display actual data queried from SQLite `students` and `attendance` database tables.
4. **Dynamic Updating**: Charts MUST update automatically when attendance data changes or when filters/dates are refreshed.
5. **CPU-First & Offline**: Charts MUST render locally using lightweight Python tools (e.g. Matplotlib embedded in CustomTkinter via `FigureCanvasTkAgg` or native Tkinter Canvas rendering). Zero cloud chart APIs or external web calls.

---

## Required Features

1. **Analytics Service Layer (`app/analytics/service.py` & `app/analytics/__init__.py`)**:
   - `get_daily_attendance_trend(days=7, db_path=None)`: returns daily count breakdown for the past N days.
   - `get_status_distribution(attendance_date=None, db_path=None)`: returns status count proportions (Present, Absent, Late, Excused).
   - `get_monthly_attendance_trend(months=6, db_path=None)`: aggregates monthly average attendance rates.
   - `get_student_risk_analytics(db_path=None)`: categorizes active students into performance bands (>90%, 75-90%, <75%).
2. **Canvas Chart Renderer & Analytics View UI (`app/analytics/chart_renderer.py` & `app/ui/analytics.py`)**:
   - `AnalyticsViewFrame`: Interactive CustomTkinter view displaying 4 chart panels:
     - Panel 1: Daily Attendance Trend (Bar/Line chart)
     - Panel 2: Status Proportions Distribution (Donut/Pie chart)
     - Panel 3: Monthly Attendance Rate Trend (Line chart)
     - Panel 4: Student Attendance Risk Breakdown (Bar chart)
   - Controls: Date range selector, trend period dropdown (7 Days, 14 Days, 30 Days), and Refresh button.
3. **Integration with Main Application Layout (`app/ui/main_window.py`)**:
   - Connect "Analytics & Charts" tab in top-level navigation layout.
4. **Automated Test Suite (`tests/test_stage9_analytics.py`)**:
   - Automated unit & integration tests verifying analytics queries, trend calculations, zero-data safety, RBAC authorization, and dynamic database update reflection.

---

## Existing Components Reused
- `app/database/`: `get_attendance_by_date`, `list_students`, `get_db_connection`.
- `app/auth/`: `get_session()`, `SessionManager` (backend RBAC authorization).
- `app/reports/`: `get_student_attendance_summary()`.
- `app/ui/`: CustomTkinter UI framework.

---

## New Components
- **`app/analytics/service.py`**: Analytics service layer computing daily trends, status distributions, monthly trends, and student risk bands under RBAC.
- **`app/analytics/chart_renderer.py`**: Lightweight Matplotlib / Tkinter Canvas chart rendering module.
- **`app/analytics/__init__.py`**: Package initialization exposing analytics service and chart functions.
- **`app/ui/analytics.py`**: Dedicated CustomTkinter Visual Analytics View component (`AnalyticsViewFrame`).
- **`tests/test_stage9_analytics.py`**: Dedicated automated test suite for Stage 9 Analytics System.

---

## Database Changes
- **No Schema Changes Required**.
- Operates on existing Stage 1 SQLite `students` and `attendance` tables.

---

## AI Integration
- Reuses existing Stage 4 AI engine status and threshold configurations where appropriate.

---

## Authentication/RBAC
- Backend service methods (`get_daily_attendance_trend`, `get_status_distribution`, `get_monthly_attendance_trend`, `get_student_risk_analytics`) enforce active session validation via `_require_authenticated_user()`. Unauthenticated calls throw `PermissionError`.

---

## UI
- `AnalyticsViewFrame` (`app/ui/analytics.py`) featuring:
  - Header controls (Time Horizon Dropdown: 7 Days, 14 Days, 30 Days; Refresh Button)
  - 4 Chart Grid Cards (Daily Trend, Status Distribution, Monthly Trend, Student Performance Bands)

---

## Security
- **Local Rendering Only**: Matplotlib / Tkinter Canvas renders charts strictly in local RAM.
- **Zero Remote Telemetry or Cloud Chart Services**: 100% offline local processing.
- **Parameterized SQL**: All aggregation queries use parameterized bindings (`?`).
- **Zero Sensitive Data Exposure**: Charts display aggregated numerical counts and percentages. Zero biometric data, face vectors, or secrets are rendered or logged.

---

## Performance
- Target System: Intel Core i3-12100 CPU, 12 GB RAM, Integrated Intel UHD 730, Windows 10.
- Chart Computation & Render Latency: < 40 ms total.
- Memory Overhead: < 3.0 MB RAM allocation.

---

## Testing
- Automated test suite in `tests/test_stage9_analytics.py`:
  - RBAC authorization check
  - Daily trend aggregation accuracy (Past N days)
  - Status distribution percentage accuracy
  - Monthly trend calculation accuracy
  - Student risk categorization (>90%, 75-90%, <75%)
  - Empty database / zero-data chart dataset safety
  - Dynamic update reflection when new attendance records are added

---

## Documentation
- `docs/STAGE_9_IMPLEMENTATION_PLAN.md` (this plan)
- `docs/STAGE_9_IMPLEMENTATION.md`
- `docs/STAGE_9_TESTING.md`
- `docs/STAGE_9_REPORT.md`
- `docs/ANALYTICS_AND_CHARTS.md`

---

## Implementation Substages
- **9A**: Analytics Service Layer (`app/analytics/service.py`, `app/analytics/__init__.py`).
- **9B**: Chart Renderer & CustomTkinter Analytics View UI (`app/analytics/chart_renderer.py` & `app/ui/analytics.py`).
- **9C**: UI Navigation Integration connecting Analytics View with top-level main window navigation layout.
- **9D**: Comprehensive Automated Test Suite (`tests/test_stage9_analytics.py`) & Documentation.

---

## Exit Criteria
- [ ] Daily attendance trend chart correctly aggregates Present and Absent counts over time.
- [ ] Status distribution chart accurately displays Present, Absent, Late, and Excused proportions.
- [ ] Monthly attendance trend chart correctly displays monthly average attendance rates.
- [ ] Student performance distribution chart correctly categorizes high-performing and at-risk students.
- [ ] Charts dynamically update when underlying database attendance data changes.
- [ ] Session RBAC authorization enforced at backend service layer.
- [ ] All existing (105) and new Stage 9 tests pass (target: 112+ tests).
- [ ] Application startup verified (`main.py`).
- [ ] Working tree clean, zero secrets/biometric photos committed, Git checkpoint created.

---

## Risks
- **None identified**. Matplotlib is a standard Python desktop library compatible with Tkinter/CustomTkinter (`FigureCanvasTkAgg`).

---

## Rollback Strategy
If any regression occurs during Stage 9 development, revert to git commit `17306e0` (`stage-8: implement attendance reports and export`).
