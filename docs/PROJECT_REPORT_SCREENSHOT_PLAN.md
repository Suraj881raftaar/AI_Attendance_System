# Project Report Screenshot Plan — AI-Enabled Smart Attendance System

## Executive Overview

This document specifies the official **Screenshot Plan** for the **AI-Enabled Smart Attendance System** project report. In accordance with academic documentation standards and strict repository guidelines, visual placeholders are provided for each of the 10 required core application interface screens.

Each entry details:
- **Screenshot Number & Identifier**
- **Target Interface Screen / Window**
- **Visible Elements & UI Controls**
- **Educational / Evaluative Purpose**
- **Suggested Print Caption**
- **Standardized Placeholder Representation**

---

## Required Application Interface Screenshot Specifications

### Screenshot 1: User Login Screen
- **Screen**: `LoginWindow` (`app/ui/login.py`)
- **Visible Elements**:
  - Central dark-theme authentication card with application logo icon.
  - Heading: `"AI-Enabled Smart Attendance System - User Login"`.
  - Username text entry field (`CTkEntry`).
  - Password text entry field (`CTkEntry` with masked character display).
  - Primary `"Login"` button (`CTkButton` in primary blue accent `#1F497D`).
  - Status notification bar showing `"Ready"` or authentication failure messages in red.
- **Purpose**: Demonstrates system security, user authentication entry point, and dark-mode aesthetic styling.
- **Suggested Caption**: *Figure 1: User Authentication and Login Interface (`LoginWindow`).*
- **Placeholder**:
  ```text
  [SCREENSHOT PLACEHOLDER #1: User Login Screen (LoginWindow)]
  ```

---

### Screenshot 2: First-Run Administrator Setup
- **Screen**: First-Run Setup Mode in `LoginWindow` (`app/ui/login.py`)
- **Visible Elements**:
  - Special configuration banner: `"First-Run System Initialization — Create Admin Account"`.
  - Username entry field (`"admin"` default suggestion).
  - Password entry field.
  - Confirm Password entry field.
  - Action button: `"Create Admin Account & Initialize System"`.
  - Informative text explaining that this account gains full administrator privileges (`ADMIN` role).
- **Purpose**: Illustrates automatic database seeding and first-time system deployment workflow.
- **Suggested Caption**: *Figure 2: First-Run Administrator Account Creation Setup.*
- **Placeholder**:
  ```text
  [SCREENSHOT PLACEHOLDER #2: First-Run Admin Setup Window]
  ```

---

### Screenshot 3: Management Dashboard
- **Screen**: `DashboardViewFrame` (`app/ui/dashboard.py`) inside `MainWindow` shell.
- **Visible Elements**:
  - Unified Application Shell topbar with user indicator (`"Admin [ADMIN]"`) and AI badge (`"AI Status: MODEL AVAILABLE"`).
  - 4 Key Summary Metric Cards:
    1. **Total Registered Students** (e.g. `45`)
    2. **Present Today** (e.g. `38`)
    3. **Absent Today** (e.g. `7`)
    4. **Attendance Rate %** (e.g. `84.4%`)
  - **Recent Attendance Activity Table**: Live scrollable list showing recent recognition logs (Time, Student ID, Name, Class/Section, Status, Confidence Score).
  - **Quick Action Navigation Buttons**: `"Start AI Attendance"`, `"Register New Student"`, `"View Reports"`.
- **Purpose**: Showcases executive summary metrics, real-time activity feed, and central dashboard control.
- **Suggested Caption**: *Figure 3: Main Management Dashboard View with Summary Cards and Activity Table.*
- **Placeholder**:
  ```text
  [SCREENSHOT PLACEHOLDER #3: Management Dashboard (DashboardViewFrame)]
  ```

---

### Screenshot 4: Student Management & Profile List
- **Screen**: `StudentManagementFrame` (`app/ui/students.py`)
- **Visible Elements**:
  - Filter & Search Header: Search input (`CTkEntry`), Class filter dropdown (`"All Classes"`, `"12"`), Section filter dropdown (`"All Sections"`, `"A"`), Status filter (`"Active"`).
  - Action Buttons: `"Add New Student"`, `"Refresh List"`.
  - **Student Information Table**: Columns for Student Code (`STU-101`), Full Name, Class, Section, Roll Number, Phone, Face Status (`"Enrolled"` / `"Not Registered"`), and Action Buttons (`"Edit"`, `"Register Face"`, `"Deactivate"`).
- **Purpose**: Displays CRUD student profile management, tabular layout, and face enrollment status tracking.
- **Suggested Caption**: *Figure 4: Student Management View displaying registered student profiles.*
- **Placeholder**:
  ```text
  [SCREENSHOT PLACEHOLDER #4: Student Management Interface (StudentManagementFrame)]
  ```

---

### Screenshot 5: Face Biometric Registration Window
- **Screen**: `StudentFaceRegistrationWindow` (`app/ui/registration_view.py`)
- **Visible Elements**:
  - Student Profile Banner: Name (e.g. `"Rahul Sharma"`), Code (`STU-101`), Class/Section (`12-A`).
  - Live Camera Preview Canvas: Live video feed showing YuNet face detection bounding box (green square) and 5 facial landmark points.
  - **5-Sample Progress Indicator**: Visual progress bar (`0/5` to `5/5`) and 5 sample thumbnail slots.
  - Quality Assessment Labels: Real-time feedback (`"Bounding Box Size: 140x140 OK"`, `"Laplacian Variance Sharpness: 48.2 (Passed >= 25.0)"`).
  - Action Buttons: `"Capture Sample"`, `"Save Face Biometric Template"`, `"Cancel"`.
- **Purpose**: Demonstrates 5-sample automated quality-checked biometric enrollment workflow.
- **Suggested Caption**: *Figure 5: Student Face Biometric Registration Preview Modal (`StudentFaceRegistrationWindow`).*
- **Placeholder**:
  ```text
  [SCREENSHOT PLACEHOLDER #5: Face Biometric Registration Modal]
  ```

---

### Screenshot 6: Real-Time AI Attendance Recognition Stream
- **Screen**: `AttendanceViewFrame` (`app/ui/attendance.py`)
- **Visible Elements**:
  - Input Source Selector: Dropdown choices (`"Camera 0 (Default Webcam)"`, `"Image File"`, `"Video File"`, `"Mobile Camera (DroidCam)"`).
  - Stream Control Buttons: `"Start Attendance Stream"` (green), `"Stop Stream"` (red).
  - **Live OpenCV Video Stream Canvas**:
    - Recognized Face: Green bounding box around detected face, overlay label (`"STU-101: Rahul Sharma (0.84)"`).
    - Unknown Face: Red bounding box around detected face, overlay label (`"Unknown (0.24)"`).
  - **Live Recognition Feed Log**: Side panel showing real-time event log (`"[10:15:22] Recognized: Rahul Sharma (STU-101) - Marked Present"`).
- **Purpose**: Illustrates real-time YuNet detection, SFace 128D embedding matching ($\ge 0.363$), 10s safety cooldown, and live UI bounding box rendering.
- **Suggested Caption**: *Figure 6: Real-Time AI Face Recognition Stream with Bounding Box Overlay and Live Log.*
- **Placeholder**:
  ```text
  [SCREENSHOT PLACEHOLDER #6: Real-Time AI Attendance Engine View]
  ```

---

### Screenshot 7: Attendance Reports & Search Filtering
- **Screen**: `ReportsViewFrame` (`app/ui/reports.py`)
- **Visible Elements**:
  - Multi-Criteria Search & Filter Panel: Start Date (`YYYY-MM-DD`), End Date (`YYYY-MM-DD`), Student Query (`CTkEntry`), Class Filter, Status Filter (`"Present"`, `"Absent"`, `"Late"`, `"Excused"`).
  - Filter Action Button: `"Apply Filters"`, `"Reset Filters"`.
  - **Attendance Log Data Grid**: Columns for Log ID, Date, Time, Student Code, Student Name, Class/Section, Status, Confidence Score, Recognition Method (`"automatic"` / `"manual"`), and Actions (`"Correct Status"`).
  - Exporter Action Buttons: `"Export to CSV"` (blue), `"Export to Excel (.xlsx)"` (green).
- **Purpose**: Highlights multi-criteria search filtering, tabular reporting, and manual attendance status correction capability.
- **Suggested Caption**: *Figure 7: Attendance Reports Interface with Multi-Criteria Filtering and Data Grid.*
- **Placeholder**:
  ```text
  [SCREENSHOT PLACEHOLDER #7: Attendance Reports View (ReportsViewFrame)]
  ```

---

### Screenshot 8: Excel / CSV Exported Reports
- **Screen**: Output Files generated by `app/reports/exporter.py` opened in Excel / Spreadsheet Viewer.
- **Visible Elements**:
  - OpenPyXL Multi-Sheet Excel Workbook (`Attendance_Report_YYYY-MM-DD.xlsx`):
    - Sheet 1 (`"Attendance Log"`): Styled header row (dark blue background `#1F497D`, bold white text), formatted date/time columns, colored status cells (Green for `"Present"`, Red for `"Absent"`).
    - Sheet 2 (`"Student Summary"`): Student Code, Student Name, Class/Section, Total Days, Present Days, Absent Days, Attendance Percentage %.
  - Alternative CSV file view in text editor.
- **Purpose**: Validates automated OpenPyXL report generation, styled formatting, and multi-sheet data exporting.
- **Suggested Caption**: *Figure 8: Generated Multi-Sheet OpenPyXL Excel Workbook Export.*
- **Placeholder**:
  ```text
  [SCREENSHOT PLACEHOLDER #8: Exported Excel Workbook (.xlsx) Report Output]
  ```

---

### Screenshot 9: Visual Analytics & Chart Grid
- **Screen**: `AnalyticsViewFrame` (`app/ui/analytics.py`)
- **Visible Elements**:
  - Timeframe Selector: Tab choices (`"Past 7 Days"`, `"Past 14 Days"`, `"Past 30 Days"`).
  - Action Button: `"Refresh Analytics Charts"`.
  - **2x2 Matplotlib Visual Analytics Chart Canvas** (`chart_renderer.py`):
    - **Chart 1 (Top-Left)**: *Daily Attendance Trend* (Bar/Line chart showing Present vs Absent counts per day).
    - **Chart 2 (Top-Right)**: *Status Distribution* (Donut chart showing % breakdown of Present, Absent, Late, Excused).
    - **Chart 3 (Bottom-Left)**: *Monthly Attendance Trend* (Line chart tracking average monthly attendance rates).
    - **Chart 4 (Bottom-Right)**: *Student Performance Distribution* (Categorical bar chart showing student risk categories: Excellent `>90%`, Good `75-90%`, At-Risk `<75%`).
- **Purpose**: Demonstrates data visualization capability, statistical aggregation, and embedded Matplotlib canvas integration.
- **Suggested Caption**: *Figure 9: Visual Analytics View displaying 2x2 Matplotlib Chart Panel.*
- **Placeholder**:
  ```text
  [SCREENSHOT PLACEHOLDER #9: Visual Analytics 2x2 Chart Grid (AnalyticsViewFrame)]
  ```

---

### Screenshot 10: Action Confirmation Dialog & Logout
- **Screen**: `ConfirmationDialog` (`app/ui/components.py`) modal popup over `MainWindow`.
- **Visible Elements**:
  - Dimmed background overlay behind modal card.
  - Dialog Title: `"Confirm System Logout"`.
  - Message: `"Are you sure you want to end your active session and log out of the AI Attendance System?"`.
  - Action Buttons: `"Cancel"` (secondary gray), `"Logout"` (warning red/orange).
- **Purpose**: Shows modal UI dialog hardening, session destruction confirmation, and application safety controls.
- **Suggested Caption**: *Figure 10: Modal Action Confirmation Dialog (`ConfirmationDialog`).*
- **Placeholder**:
  ```text
  [SCREENSHOT PLACEHOLDER #10: Modal Logout Confirmation Dialog]
  ```

---

## Summary Table of Screenshots

| Screenshot # | Target View / Window | Module Path | Purpose |
| :---: | :--- | :--- | :--- |
| **1** | User Login | `app/ui/login.py` | Authentication & security entry point |
| **2** | First-Run Setup | `app/ui/login.py` | Admin account creation & DB initialization |
| **3** | Dashboard Overview | `app/ui/dashboard.py` | Summary metrics & live activity feed |
| **4** | Student Management | `app/ui/students.py` | Student profile CRUD & face status tracking |
| **5** | Face Registration | `app/ui/registration_view.py` | 5-sample quality-checked face enrollment |
| **6** | AI Attendance Engine | `app/ui/attendance.py` | Real-time recognition, bounding boxes & 10s cooldown |
| **7** | Attendance Reports | `app/ui/reports.py` | Multi-criteria search filtering & status correction |
| **8** | Excel / CSV Export | `app/reports/exporter.py` | OpenPyXL multi-sheet Excel report output |
| **9** | Visual Analytics | `app/ui/analytics.py` | 2x2 Matplotlib chart grid visualization |
| **10** | Confirmation Modal | `app/ui/components.py` | Modal safety dialog & session logout |
