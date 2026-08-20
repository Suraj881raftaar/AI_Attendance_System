# User Operational Manual

## 1. Introduction

Welcome to the AI-Enabled Smart Attendance System user operational manual. This document guides Teachers and Administrators through day-to-day operations, student enrollment, AI attendance processing, report filtering, data exports, and visual analytics.

---

## 2. Authentication & First-Run Setup

### First-Run Setup:
1. Launch application via `run_app.bat`.
2. On first launch, if no administrator account exists, the First-Run Setup Window appears.
3. Enter desired Administrator Username (e.g. `admin`), Password, and Full Name.
4. Click **Create Administrator Account**.

### Login:
1. Enter Username and Password.
2. Select Role (`Admin` or `Teacher`).
3. Click **Login**. Upon successful authentication, the main application shell opens to the **Dashboard**.

---

## 3. Navigation Shell Structure

The left sidebar provides access to 5 main view modules:
- **Dashboard**: High-level overview and summary statistics.
- **Students**: Student registration, face biometric enrollment, detail edits, and deactivations.
- **AI Attendance**: Live real-time camera recognition and automatic attendance marking.
- **Reports**: Searchable attendance record logs, manual corrections, and CSV/Excel exports.
- **Analytics**: Matplotlib visual trend charts and student performance categorization.

The topbar header displays the logged-in username, role badge (`[ADMIN]` or `[TEACHER]`), AI model engine status (`AI Status: MODEL AVAILABLE`), and the **Logout** button.

---

## 4. Student Management & Face Registration

### Adding a New Student:
1. Navigate to **Students** view.
2. Click **Add New Student**.
3. Fill in Student Code (e.g. `STU-101`), Name, Class, Section, Roll Number, and Guardian Contact.
4. Click **Save Student**.

### Face Biometric Enrollment:
1. Select a student in the student list and click **Enroll Face**.
2. The Face Registration Window opens with video/camera preview.
3. Align student face in camera frame. The AI engine automatically captures 5 high-quality face samples.
4. Once 5 samples are collected, the 128D feature embedding vector is saved to local SQLite database.

---

## 5. AI Attendance Camera View

1. Navigate to **AI Attendance** view.
2. Select Video Source (`Camera 0`, `Image Mode`, `Video Mode`, or `Mobile Camera`).
3. Click **Start Attendance Camera**.
4. The AI recognition engine automatically detects faces (green bounding box), extracts 128D embeddings, compares against enrolled database records ($\ge 0.363$), and records attendance (`Present`).
5. A 10-second safety cooldown prevents repeated duplicate logs, while SQLite enforces one attendance record per student per day.

---

## 6. Reports & Data Exports

1. Navigate to **Reports** view.
2. Use filter bar to search by Start Date, End Date, Student Name/ID, Class, or Status (`Present`, `Absent`, `Late`, `Excused`).
3. **Manual Correction**: Click **Correct** next to any record to update status or time under administrator authorization.
4. **CSV Export**: Click **Export CSV** to save current filtered records to `.csv` format.
5. **Excel Export**: Click **Export Excel** to save a styled multi-tab `.xlsx` workbook (Attendance Records + Student Summary tabs).

---

## 7. Session Logout

Click **Logout** in the topbar header. A confirmation dialog appears. Confirming clears the RAM session token and returns the application to the Login Window.
