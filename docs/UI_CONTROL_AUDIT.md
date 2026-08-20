# UI Control & Navigation Audit Report

## 1. Overview & UI Scope
This document provides a complete control-by-control, view-by-view audit of the CustomTkinter desktop interface in the AI-Enabled Smart Attendance System.

---

## 2. Exhaustive UI Control Inventory

| View / Dialog | Control / Widget | Widget Type | Purpose & Action | Callback Function | Target Function / Module | Validation & Error Handling | Health Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **LoginWindow** | Username Entry | `CTkEntry` | Accepts login/admin username input | None (Direct input) | `LoginFrame.username_entry.get()` | Validated non-empty on submit | **GREEN** |
| **LoginWindow** | Password Entry | `CTkEntry` | Accepts user password input | None (Direct input) | `LoginFrame.password_entry.get()` | Masked `*`, validated non-empty | **GREEN** |
| **LoginWindow** | Create Admin & Login Button | `CTkButton` | Triggers first-run setup | `_handle_first_run_setup` | `app.auth.setup_first_admin` + `login` | Validates non-empty credentials; raises `ValueError` | **GREEN** |
| **LoginWindow** | Login Button | `CTkButton` | Triggers authentication | `_handle_login` | `app.auth.login` | Validates credentials; raises `ValueError` | **GREEN** |
| **LoginWindow** | Topbar Window Close / Destroy | Window Event | Destroys authentication window | `_handle_success` | `LoginWindow.destroy()` | **ORANGE**: Standard `destroy()` can raise `_tkinter.TclError` if window is already closed before callback completes. | **ORANGE** |
| **MainWindow** | Topbar Title Label | `CTkLabel` | Displays application name & version | None | Static Label | Static rendering | **GREEN** |
| **MainWindow** | User Role Badge | `CTkLabel` | Displays logged-in user & role | None | `SessionManager.get_current_user()` | Updates dynamically on login | **GREEN** |
| **MainWindow** | AI Model Status Indicator | `CTkLabel` | Displays local ONNX model status | None | `app.ai.config.get_ai_runtime_status` | Renders `MODEL AVAILABLE` or `MODEL MISSING` | **GREEN** |
| **MainWindow** | Topbar Logout Button | `CTkButton` | Displays confirmation dialog | `_confirm_logout` | `ConfirmationDialog` | Modal dialog confirmation | **GREEN** |
| **Sidebar Menu** | Dashboard Navigation Tab | `CTkButton` | Switches view to Dashboard | `_show_dashboard` | `MainWindow._switch_view` | Re-renders `DashboardViewFrame` | **GREEN** |
| **Sidebar Menu** | Students Navigation Tab | `CTkButton` | Switches view to Student List | `_show_students` | `MainWindow._switch_view` | Re-renders `StudentManagementFrame` | **GREEN** |
| **Sidebar Menu** | AI Attendance Navigation Tab | `CTkButton` | Switches view to Live AI Attendance | `_show_attendance` | `MainWindow._switch_view` | Re-renders `AttendanceViewFrame` | **GREEN** |
| **Sidebar Menu** | Reports Navigation Tab | `CTkButton` | Switches view to Reports | `_show_reports` | `MainWindow._switch_view` | Re-renders `ReportsViewFrame` | **GREEN** |
| **Sidebar Menu** | Analytics Navigation Tab | `CTkButton` | Switches view to Visual Analytics | `_show_analytics` | `MainWindow._switch_view` | Re-renders `AnalyticsViewFrame` | **GREEN** |
| **DashboardViewFrame** | Stat Card: Total Students | Card Frame | Shows active registered student count | None | `app.dashboard.get_dashboard_metrics` | Handles 0 count safely | **GREEN** |
| **DashboardViewFrame** | Stat Card: Present Today | Card Frame | Shows today's present count | None | `app.dashboard.get_dashboard_metrics` | Computes from SQLite | **GREEN** |
| **DashboardViewFrame** | Stat Card: Absent Today | Card Frame | Shows today's absent count | None | `app.dashboard.get_dashboard_metrics` | Active students minus present | **GREEN** |
| **DashboardViewFrame** | Stat Card: Attendance % | Card Frame | Shows overall percentage | None | `app.dashboard.get_dashboard_metrics` | Protected against division by zero | **GREEN** |
| **DashboardViewFrame** | Recent Activity Table | Scroll Frame | Displays recent attendance logs | None | `app.dashboard.get_dashboard_metrics` | Renders empty state if no activity | **GREEN** |
| **StudentManagementFrame**| Search Box | `CTkEntry` | Filters student list by query | `_on_search` | `app.students.search_students` | Live filter on key release | **GREEN** |
| **StudentManagementFrame**| Add New Student Button | `CTkButton` | Opens student creation modal | `_open_add_student_dialog` | Custom Modal Dialog | Form input validation (`validate_student_inputs`) | **GREEN** |
| **StudentManagementFrame**| Edit Student Button | `CTkButton` | Opens student modification modal | `_open_edit_student_dialog` | Custom Modal Dialog | Validates non-empty name & roll | **GREEN** |
| **StudentManagementFrame**| Deactivate Student Button | `CTkButton` | Deactivates student record | `_deactivate_student` | `ConfirmationDialog` -> `app.students.deactivate_student_record` | Prevents accidental deletion | **GREEN** |
| **StudentManagementFrame**| Enroll Face Button | `CTkButton` | Opens Face Registration Window | `_open_face_registration` | `StudentFaceRegistrationWindow` | Opens 5-sample video capture window | **GREEN** |
| **RegistrationWindow** | Start Capture Button | `CTkButton` | Starts 5-sample AI collection | `_start_capture` | `FaceEnrollmentManager` | Quality check (face size $\ge 60\times 60$, sharpness $\ge 25$) | **GREEN** |
| **RegistrationWindow** | Re-enroll Face Button | `CTkButton` | Overwrites existing face embedding | `_reregister` | `ConfirmationDialog` -> `FaceEnrollmentManager` | Transactional overwrite | **GREEN** |
| **RegistrationWindow** | De-register Face Button | `CTkButton` | Soft-deletes face data | `_deregister` | `ConfirmationDialog` -> `app.students.deregister_student_face` | Updates DB status to `'inactive'` | **GREEN** |
| **AttendanceViewFrame** | Video Source Combo | `CTkOptionMenu`| Selects frame provider source | `_on_source_change` | `Camera`, `Image`, `Video`, `Mobile` | Updates active `FrameProvider` | **GREEN** |
| **AttendanceViewFrame** | Start Camera Button | `CTkButton` | Begins real-time AI recognition loop| `_start_camera` | `AIRecognitionPipeline` | Checks model presence; handles disconnect | **GREEN** |
| **AttendanceViewFrame** | Stop Camera Button | `CTkButton` | Stops AI video processing thread | `_stop_camera` | `AIRecognitionPipeline.stop()` | Safely releases camera feed | **GREEN** |
| **AttendanceViewFrame** | Video Stream Canvas | `CTkLabel` | Renders video frames & bounding boxes| `_update_frame` | PIL Image conversion | Overlays green (known) / red (unknown) boxes | **GREEN** |
| **ReportsViewFrame** | Filter Start / End Date | `CTkEntry` | Filters by date range | `_apply_filters` | `app.reports.search_attendance_records` | Formats `YYYY-MM-DD` | **GREEN** |
| **ReportsViewFrame** | Filter Status Combo | `CTkOptionMenu`| Filters by `Present`, `Absent`, etc. | `_apply_filters` | `app.reports.search_attendance_records` | Defaults to All | **GREEN** |
| **ReportsViewFrame** | Correct Record Button | `CTkButton` | Opens manual correction modal | `_open_correction_dialog` | `app.reports.correct_attendance_record` | Enforces RBAC & log audit | **GREEN** |
| **ReportsViewFrame** | Export CSV Button | `CTkButton` | Saves current records to CSV | `_export_csv` | `app.reports.export_attendance_csv` | File dialog save prompt | **GREEN** |
| **ReportsViewFrame** | Export Excel Button | `CTkButton` | Saves styled multi-tab workbook | `_export_excel` | `app.reports.export_attendance_excel` | Uses OpenPyXL workbook generator | **GREEN** |
| **AnalyticsViewFrame** | Timeframe Selector | `CTkSegmentedButton`| Selects 7, 14, 30 days | `_on_timeframe_change` | `app.analytics.service` | Re-calculates aggregates | **GREEN** |
| **AnalyticsViewFrame** | Matplotlib 4-Chart Grid | `Canvas` | Renders 4 statistical charts | `_render_charts` | `app.analytics.chart_renderer` | Clears previous figure canvas cleanly | **GREEN** |
| **ConfirmationDialog** | Confirm Action Button | `CTkButton` | Executes dangerous action | `_on_confirm` | Callback function | Invokes callback & destroys modal | **GREEN** |
| **ConfirmationDialog** | Cancel Button | `CTkButton` | Cancels action | `_on_cancel` | None | Destroys modal without executing action | **GREEN** |

---

## 3. UI Lifecycle & Font Instantiation Audit Findings

### Finding UI-1: CustomTkinter `CTkFont` Initialization Sequence
- **Issue**: In `app/ui/dashboard.py` (line 60), `app/ui/components.py` (line 67), and `app/ui/main_window.py`, `CTkFont` instances are instantiated inside widget constructors. If a custom component is instantiated or font configuration occurs before Tkinter initializes its root window or after a parent window is destroyed, Tkinter raises:
  `RuntimeError: Too early to use font: no default root window`
- **Severity**: **ORANGE**
- **Impact**: Occurs if widgets are instantiated asynchronously outside the main thread or after window teardown.
- **Recommendation**: Wrap font usage or ensure widget construction strictly occurs within active parent Tkinter root window lifecycles.

### Finding UI-2: `destroy()` Call on Already-Destroyed Window in Login Callback
- **Issue**: In `app/ui/login.py` (line 159), `LoginWindow._handle_success` calls `self.destroy()`. If the user closes the window via topbar 'X' while authentication is processing, `self.destroy()` raises `_tkinter.TclError: can't invoke "destroy" command: application has been destroyed`.
- **Severity**: **ORANGE**
- **Impact**: Intermittent TclError in console logs during rapid window closing.
- **Recommendation**: Guard `destroy()` calls with `if self.winfo_exists(): self.destroy()`.
