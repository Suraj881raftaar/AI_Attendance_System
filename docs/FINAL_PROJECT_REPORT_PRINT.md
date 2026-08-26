# AI-ENABLED SMART ATTENDANCE SYSTEM
## Academic Project Report — CBSE Class 12 Computer Science (083)

---

# 1. COVER PAGE

**PROJECT TITLE:**
AI-Enabled Smart Attendance System

**SUBMITTED BY:**
Student Name: `[STUDENT NAME PLACEHOLDER]`
Class: Senior Secondary (Class 12 - Science / CS)
Roll Number: `[ROLL NUMBER PLACEHOLDER]`
Academic Session: `[SESSION PLACEHOLDER]`

**SUBMITTED TO:**
Department of Computer Science
School Name: `[SCHOOL NAME PLACEHOLDER]`
Subject: Computer Science (Code: 083)

---

# 2. CERTIFICATE

```text
================================================================================
                               CERTIFICATE
================================================================================

This is to certify that Master/Miss _______________________________________, 
Roll No. ________________________, a student of Class XII (Computer Science) 
of ____________________________________________________________________ School, 
has successfully completed the academic project titled "AI-Enabled Smart 
Attendance System" under the guidance and supervision of 
___________________________________ (Teacher In-Charge) during the academic 
session ______________ in partial fulfillment of the requirements for the 
CBSE Senior School Certificate Examination (SSCE) in Computer Science (083).



___________________________                     ___________________________
Teacher In-Charge                               Internal / External Examiner



___________________________
Principal Signature & School Seal
================================================================================
```

---

# 3. DECLARATION

I hereby declare that the academic project titled **"AI-Enabled Smart Attendance System"** submitted for the Class 12 CBSE Computer Science examination is an original work developed by me under the guidance of my Computer Science teacher. 

This project is submitted strictly for academic evaluation. No part of this project has been copied from any unauthorized source, and all open-source libraries, models, and references used have been properly cited and acknowledged.

Student Signature: ___________________________
Student Name: `[STUDENT NAME PLACEHOLDER]`
Date: `[DATE PLACEHOLDER]`

---

# 4. ACKNOWLEDGEMENT

I express my sincere gratitude to my Computer Science Teacher, `[TEACHER NAME PLACEHOLDER]`, for their valuable guidance, continuous support, and constructive feedback throughout the development of this project.

I am also thankful to our Principal, `[PRINCIPAL NAME PLACEHOLDER]`, and the management of `[SCHOOL NAME PLACEHOLDER]` for providing access to computer laboratory infrastructure and necessary software resources.

Finally, I express my appreciation to my parents and classmates for their encouragement and support during the design, coding, testing, and documentation of this academic project.

---

# 5. ABSTRACT

Traditional student attendance management in secondary schools relies on manual paper registers, which consume valuable instructional time (5–10 minutes per period), are prone to human entry errors and proxy attendance, and make record auditing cumbersome.

The **AI-Enabled Smart Attendance System** is an offline, CPU-optimized, privacy-conscious desktop application built to automate classroom attendance taking using computer vision and deep neural networks. Built with **Python 3.13**, **CustomTkinter**, **OpenCV**, and **SQLite 3**, the system operates 100% locally without requiring external cloud servers, GPU hardware, or subscription APIs.

The AI pipeline employs **YuNet** for real-time edge face detection ($640 \times 480$ resolution) and **SFace** for 128-dimensional facial feature embedding extraction. Face matching is performed using Cosine Similarity against a fixed threshold of **0.363**. Biometric face data is stored locally as 128D mathematical vectors in SQLite, while raw video frames are processed in RAM and discarded immediately to preserve student privacy.

The system incorporates an automated attendance engine featuring a 10-second safety cooldown buffer and SQLite `UNIQUE(student_id, attendance_date)` duplicate protection. It offers role-based access control (RBAC) with PBKDF2-HMAC-SHA256 authentication, student profile CRUD management, 5-sample quality-checked face registration, multi-criteria filtering, CSV and OpenPyXL Excel reporting, and a 2x2 grid of Matplotlib visual analytics charts. The application passes **131 automated unit and integration tests** (100% pass rate) and is packaged via PyInstaller for standalone deployment.

---

# 6. TABLE OF CONTENTS

- [1. Cover Page](#1-cover-page)
- [2. Certificate](#2-certificate)
- [3. Declaration](#3-declaration)
- [4. Acknowledgement](#4-acknowledgement)
- [5. Abstract](#5-abstract)
- [6. Table of Contents](#6-table-of-contents)
- [7. Introduction](#7-introduction)
- [8. Problem Statement](#8-problem-statement)
- [9. Objectives](#9-objectives)
- [10. Scope](#10-scope)
- [11. Existing System](#11-existing-system)
- [12. Proposed System](#12-proposed-system)
- [13. Hardware Requirements](#13-hardware-requirements)
- [14. Software Requirements](#14-software-requirements)
- [15. System Architecture](#15-system-architecture)
- [16. Application Modules](#16-application-modules)
- [17. Authentication and RBAC](#17-authentication-and-rbac)
- [18. Face Registration](#18-face-registration)
- [19. AI Face Recognition](#19-ai-face-recognition)
- [20. Mathematical Explanation](#20-mathematical-explanation)
- [21. Attendance Engine](#21-attendance-engine)
- [22. Database Design](#22-database-design)
- [23. Management Dashboard](#23-management-dashboard)
- [24. Reports and Export](#24-reports-and-export)
- [25. Visual Analytics](#25-visual-analytics)
- [26. User Interface](#26-user-interface)
- [27. Camera System](#27-camera-system)
- [28. Security and Privacy](#28-security-and-privacy)
- [29. Testing](#29-testing)
- [30. Real-World Acceptance Test](#30-real-world-acceptance-test)
- [31. Code Quality and Hardening](#31-code-quality-and-hardening)
- [32. Limitations](#32-limitations)
- [33. Future Scope](#33-future-scope)
- [34. Advantages](#34-advantages)
- [35. Disadvantages](#35-disadvantages)
- [36. Application Screenshots](#36-application-screenshots)
- [37. Results](#37-results)
- [38. Conclusion](#38-conclusion)
- [39. Viva Preparation](#39-viva-preparation)
- [40. References](#40-references)

---

# 7. INTRODUCTION

Educational institutions traditionally rely on roll-call attendance to record student participation. While simple, manual record-keeping imposes significant operational inefficiencies in modern academic environments. Teachers must spend 5 to 10 minutes of every period calling out student names and manually marking attendance logs.

Advances in Computer Vision (CV) and Artificial Intelligence (AI) provide an opportunity to modernize attendance management. By utilizing deep learning models capable of recognizing human faces in real-time camera streams, student attendance can be captured automatically as students enter the classroom.

However, existing commercial facial recognition software often requires high-end graphics processing units (GPUs), continuous cloud internet connectivity, and third-party subscription plans. Furthermore, uploading student facial photographs to cloud servers introduces significant data privacy risks.

The **AI-Enabled Smart Attendance System** addresses these challenges by delivering an **offline-first, CPU-optimized, privacy-respecting desktop system**. Developed specifically for Senior Secondary computer science evaluation, the project demonstrates how modern AI libraries and relational databases can be integrated into a secure software application running on standard school computers.

---

# 8. PROBLEM STATEMENT

Manual attendance management in schools faces several major operational challenges:

1. **Time Consumption**: Roll call consumes 5–10 minutes per period, reducing overall instructional time across the academic year.
2. **Vulnerability to Human Error & Proxy**: Teachers may mishear responses, mark wrong rows in paper registers, or fail to spot students answering proxy attendance for absent peers.
3. **Difficult Record Management**: Paper registers are easily damaged, misplaced, or filled with illegible handwriting.
4. **Labor-Intensive Reporting**: Compiling monthly attendance percentages, class summaries, or low-attendance risk reports requires manually counting register entries, taking hours of teacher effort.
5. **Privacy & Infrastructure Barriers of Cloud AI**: Existing commercial biometrics require uploading facial photographs to external cloud APIs, violating student biometric data privacy and requiring expensive high-speed internet infrastructure.

---

# 9. OBJECTIVES

The primary objective of this academic project is to design, develop, test, and package an automated facial recognition attendance desktop application. 

Measurable sub-objectives include:
- **Offline AI Pipeline**: Implement real-time face detection (YuNet) and feature embedding (SFace) running locally on standard CPU hardware without GPU or internet requirements.
- **Biometric Security & Privacy**: Store facial features strictly as 128-dimensional floating-point vectors in a local SQLite database, discarding raw camera frames immediately after inference.
- **Data Integrity & Duplicate Protection**: Implement a 10-second in-memory safety cooldown and an enforced SQLite database `UNIQUE(student_id, attendance_date)` constraint to prevent duplicate records.
- **Role-Based Access Control**: Secure application access using PBKDF2-HMAC-SHA256 password hashing with distinct `ADMIN` and `TEACHER` roles.
- **Reporting & Data Export**: Provide multi-criteria search filtering, interactive manual status correction, and multi-format exporting to CSV and styled multi-sheet OpenPyXL Excel workbooks.
- **Visual Analytics**: Render a 2x2 grid of statistical Matplotlib charts embedded in the CustomTkinter GUI.
- **Standalone Packaging**: Package the application into a self-contained executable distribution (`dist/AIAttendanceSystem/`) launched via `run_app.bat`.
- **Quality Verification**: Achieve a 100% pass rate across 131 automated unit, integration, hardening, and packaging tests.

---

# 10. SCOPE

### Supported Scope (In-Scope):
- Single-camera real-time video stream processing from standard USB webcams or integrated laptop cameras.
- Development-mode camera feed testing from image files, pre-recorded video files, and DroidCam USB mobile adapters.
- Student profile creation, editing, soft deactivation, and face biometric enrollment (5-sample quality-checked average).
- Automated attendance marking based on Cosine Similarity ($\ge 0.363$).
- Attendance record viewing, filtering, manual status correction, and export (CSV & Excel).
- Statistical summary dashboards and 4-panel visual analytics charts.
- Local SQLite 3 relational database storage (`data/attendance.db`).
- Standalone execution on Windows 10/11 operating systems.

### Explicitly Out-of-Scope:
- Multi-camera concurrent RTSP IP camera streaming across multiple classrooms simultaneously.
- Automated SMS / WhatsApp / Email notification gateways to guardians.
- Cloud database synchronization across distant school campuses.
- Active 3D depth-map liveness anti-spoofing detection.

---

# 11. EXISTING SYSTEM

The traditional attendance system relies entirely on physical paper registers kept by class teachers.

### Advantages of Existing Manual System:
- Zero initial software or hardware cost.
- Simple, requiring no technical training for teachers.

### Limitations of Existing Manual System:
- **High time cost**: 5–10 minutes lost per period.
- **Proxy attendance vulnerability**: Students can falsely answer for absent friends.
- **Data loss risk**: Paper registers can be torn, stained, lost, or misplaced.
- **Inconvenient analytics**: Calculating attendance percentages requires tedious manual counting.

---

# 12. PROPOSED SYSTEM

The proposed **AI-Enabled Smart Attendance System** replaces manual paper attendance registers with a desktop application that recognizes enrolled students automatically using a live camera feed.

```text
[Live Camera Stream] ──> [YuNet Face Detector] ──> [Cropped Face & Landmarks]
                                                            │
[SQLite Enrolled Vectors] ──> [Cosine Matcher (>= 0.363)] <── [SFace 128D Embedder]
                                      │
                         [Attendance Recorded in SQLite]
                                      │
                   [Dashboard & Reports UI Live Refresh]
```

### Key Highlights of Proposed System:
- **Automated Real-Time Processing**: Recognizes faces in camera streams at 25–30 FPS on standard CPUs.
- **Instant Attendance Marking**: Records attendance automatically with exact date, time, and confidence score.
- **Robust Data Integrity**: Enforces strict database-level unique constraints preventing duplicate daily entries.
- **Privacy-First Architecture**: Converts face images into 128-number mathematical vectors; raw photo frames are never saved to disk.
- **Comprehensive Reports & Analytics**: Provides instant CSV/Excel exporting and statistical visual charts.

---

# 13. HARDWARE REQUIREMENTS

The system is designed and validated for standard secondary school desktop/laptop hardware:

- **Processor (CPU)**: Intel Core i3 (10th Gen or higher) / AMD Ryzen 3 (Dual-core or Quad-core, 2.0 GHz minimum). *No GPU or CUDA hardware is required.*
- **System Memory (RAM)**: 4 GB minimum (8 GB or 12 GB recommended). Peak application RAM usage remains below **80 MB**.
- **Storage**: 500 MB available local disk space (includes Python runtime, dependencies, ONNX AI models, and SQLite database).
- **Camera (Primary Input)**: Standard USB Webcam ($640 \times 480$ resolution at 30 FPS) or integrated laptop camera.
- **Camera (Development Adapter)**: Mobile camera connection via USB tethering using DroidCam client software where supported.

---

# 14. SOFTWARE REQUIREMENTS

The application is built using Python and dependencies defined in `requirements.txt`:

- **Operating System**: Microsoft Windows 10 / 11 (64-bit).
- **Programming Language**: Python 3.13.14 (64-bit).
- **GUI Framework**: `customtkinter >= 5.2.0` (Modern dark-themed Tkinter widget framework) & `Pillow >= 10.0.0`.
- **Computer Vision & AI**: `opencv-python-headless == 5.0.0.93` (OpenCV DNN module running YuNet and SFace ONNX binaries).
- **Database Engine**: SQLite 3 (Built-in Python `sqlite3` driver).
- **Data Manipulation & Reports**: `pandas >= 2.0.0` & `openpyxl >= 3.1.0` (Multi-sheet styled Excel exporting).
- **Visual Analytics**: `matplotlib >= 3.7.0` (Embedded canvas renderer `FigureCanvasTkAgg`).
- **Testing Framework**: `pytest >= 7.4.0` (131 automated unit and integration tests).
- **Application Packaging**: `pyinstaller >= 6.0.0` (Standalone folder distribution and batch launcher `run_app.bat`).

---

# 15. SYSTEM ARCHITECTURE

The application follows a clean 5-tier **Layered Architecture** ensuring complete separation of presentation, business logic, AI processing, data access, and persistence tiers:

```text
+-----------------------------------------------------------------------+
| 1. UI PRESENTATION LAYER                                              |
|    CustomTkinter Views (MainWindow Shell, Views, Dialogs, Controls)  |
+-----------------------------------------------------------------------+
                                   │
+-----------------------------------------------------------------------+
| 2. APPLICATION SERVICE LAYER                                          |
|    Auth, Students, Attendance, Reports, Dashboard, Analytics Services |
+-----------------------------------------------------------------------+
                                   │
+-----------------------------------------------------------------------+
| 3. AI ENGINE & COMPUTER VISION LAYER                                  |
|    YuNet Detector, SFace Embedder, Cosine Matcher, Frame Providers    |
+-----------------------------------------------------------------------+
                                   │
+-----------------------------------------------------------------------+
| 4. REPOSITORY DATA ACCESS LAYER                                       |
|    Parameterized SQL Queries, Transaction Context, FK Wrappers         |
+-----------------------------------------------------------------------+
                                   │
+-----------------------------------------------------------------------+
| 5. PERSISTENCE LAYER                                                  |
|    Local SQLite 3 Relational Database (`data/attendance.db`)          |
+-----------------------------------------------------------------------+
```

1. **UI Presentation Layer**: Manages user interactions, event handling, view switching, and canvas rendering. UI frames never call raw SQL directly.
2. **Application Service Layer**: Implements core business logic, RBAC session validation, filtering, exports, and metric aggregations.
3. **AI Engine Layer**: Orchestrates video frame acquisition (`FrameProvider`), YuNet face detection, SFace 128D embedding extraction, quality checking, and Cosine Similarity matching.
4. **Repository Data Access Layer**: Encapsulates all SQL statements using 100% parameterized placeholders (`?`) inside atomic transaction blocks.
5. **Persistence Layer**: Manages connection handles to local SQLite file `data/attendance.db` with enforced referential integrity (`PRAGMA foreign_keys = ON;`).

---

# 16. APPLICATION MODULES

The application functionality is organized into 8 major functional modules:

### 1. Authentication & RBAC Module
- **Purpose**: Authenticates users and enforces role privileges (`ADMIN` vs `TEACHER`).
- **Inputs**: User credentials (username, password).
- **Processing**: Verifies password hash using PBKDF2-HMAC-SHA256; manages thread-safe `SessionManager` state.
- **Outputs**: Active user session context or authentication error.

### 2. Student Management Module
- **Purpose**: Manages student profile lifecycle.
- **Inputs**: Student Code (`STU-101`), Full Name, Class, Section, Roll Number, Phone.
- **Processing**: Validates unique constraints, inserts/updates records in SQLite `students` table, handles soft deactivation.
- **Outputs**: Confirmed student record list or validation message.

### 3. Face Registration Module
- **Purpose**: Enrolls student biometric facial feature templates.
- **Inputs**: 5 face samples captured from camera preview.
- **Processing**: Evaluates sample sharpness ($\ge 25.0$) and bounding box size ($\ge 60\times 60$), extracts 128D embeddings via SFace, averages vectors, $L_2$-normalizes, and serializes as JSON.
- **Outputs**: Enrolled `face_data` record in SQLite.

### 4. AI Attendance Engine Module
- **Purpose**: Performs real-time recognition and automatic attendance logging.
- **Inputs**: Video frame stream from `FrameProvider`.
- **Processing**: YuNet face detection $\to$ SFace 128D embedding $\to$ Cosine Similarity ($\ge 0.363$) $\to$ 10s cooldown check $\to$ SQLite insert.
- **Outputs**: Bounding box overlay on video canvas, live log entry, and new `attendance` database row.

### 5. Management Dashboard Module
- **Purpose**: Displays high-level summary metrics and recent activity.
- **Inputs**: SQLite database query metrics for current date.
- **Processing**: Calculates total students, present count, absent count, and attendance percentage.
- **Outputs**: 4 summary card widgets and scrollable recent activity table.

### 6. Reports & Export Module
- **Purpose**: Provides attendance searching, manual correction, and reporting exports.
- **Inputs**: Date ranges, class/section dropdowns, student search text, status selection.
- **Processing**: Queries filtered database rows, formats table data, executes manual status corrections, builds OpenPyXL Excel workbooks and CSV files.
- **Outputs**: Filtered data grid, exported `.xlsx` workbook, and `.csv` text file.

### 7. Visual Analytics Module
- **Purpose**: Renders statistical trends and risk distribution charts.
- **Inputs**: Timeframe selection (7, 14, 30 days).
- **Processing**: Aggregates daily trends, status percentages, monthly averages, and student performance risk bands.
- **Outputs**: Embedded 2x2 Matplotlib chart figure canvas.

### 8. Packaging & Deployment Module
- **Purpose**: Compiles application into standalone executable package.
- **Inputs**: Source code, dependencies, ONNX model binaries, UI assets.
- **Processing**: PyInstaller bundling with frozen path resolution.
- **Outputs**: Portable `dist/AIAttendanceSystem/` directory and `run_app.bat` launcher.

---

# 17. AUTHENTICATION AND RBAC

Security access is managed via Role-Based Access Control (RBAC) supporting two distinct roles:
- **`ADMIN` (Administrator)**: Full access to student CRUD management, face registration, AI attendance stream, manual corrections, user account creation, reports, and analytics.
- **`TEACHER` (Teacher)**: Access restricted to viewing student lists, running AI attendance streams, generating reports, and viewing analytics charts (cannot delete records or manage user accounts).

### Password Hashing Specification:
Passwords are hashed using **PBKDF2 with HMAC-SHA256** using 100,000 iterations and a random 16-byte salt:

$$\text{Password Hash} = \text{PBKDF2-HMAC-SHA256}(\text{password}, \text{salt}, 100000)$$

Raw plaintext passwords and hash strings are never written to log files or displayed on UI screens. When a user logs out, the in-memory session is immediately destroyed.

---

# 18. FACE REGISTRATION

Facial biometric enrollment follows a strict 5-sample quality-guided workflow:

```text
[Select Student] ──> [Open Registration Window] ──> [Capture 5 Camera Frames]
                                                            │
[Save 128D Vector to DB] <── [Average & L2 Normalize] <── [Verify Quality Checks]
```

1. **Student Selection**: Operator selects an active student profile from the Student Management table.
2. **Camera Preview**: Live camera preview opens in registration modal.
3. **Quality Checks**: For each captured sample, the system verifies:
   - **Face Presence**: Exactly one face detected by YuNet ($c \ge 0.60$).
   - **Bounding Box Size**: Width and height must be $\ge 60 \times 60$ pixels.
   - **Image Sharpness**: Laplacian variance of face crop must meet or exceed $25.0$:
     $$\text{Var}_{\text{Laplacian}} = \text{Variance}(\nabla^2 I_{\text{crop}}) \ge 25.0$$
4. **Embedding Extraction**: SFace computes a 128D floating-point vector $\mathbf{v}_k$ for each of the 5 valid samples ($k = 1 \dots 5$).
5. **Vector Averaging & $L_2$ Normalization**: The 5 vectors are averaged into a single template vector $\mathbf{v}_{\text{avg}}$ and $L_2$-normalized:
   $$\mathbf{v}_{\text{avg}} = \frac{1}{5} \sum_{k=1}^{5} \mathbf{v}_k, \quad \hat{\mathbf{v}} = \frac{\mathbf{v}_{\text{avg}}}{\|\mathbf{v}_{\text{avg}}\|_2}$$
6. **Biometric Storage**: The normalized 128D vector is serialized as a JSON string and stored in the SQLite `face_data` table linked to the student ID.

---

# 19. AI FACE RECOGNITION

The core artificial intelligence pipeline operates sequentially across 6 stages:

```text
Video Frame (640x480)
   │
   ▼
[YuNet Face Detector] ── (Conf >= 0.60) ──> Bounding Box & 5 Landmarks
   │
   ▼
[Cropping & Alignment] ──> 112x112 Tensor
   │
   ▼
[SFace Recognizer] ──> 128-Dimensional Vector v
   │
   ▼
[L2 Vector Normalization] ──> ||v|| = 1.0
   │
   ▼
[Cosine Similarity Matcher] ──> Score vs Threshold 0.363
   │
   ├── (Score >= 0.363) ──> RECOGNIZED STUDENT (Mark Present)
   └── (Score < 0.363)  ──> UNKNOWN FACE (Reject / Red Box)
```

1. **Input Video Frame**: Acquired via OpenCV `FrameProvider` at $640 \times 480$ BGR format.
2. **YuNet Face Detection**: `face_detection_yunet_2023mar.onnx` detects faces, outputting bounding box $[x, y, w, h]$, 5 landmarks (eyes, nose, mouth corners), and confidence $c \ge 0.60$.
3. **Cropping & Alignment**: Face region is cropped and aligned to $112 \times 112$ pixels.
4. **SFace Embedding Extraction**: `face_recognition_sface_2021dec.onnx` transforms the aligned crop into a 128D feature embedding vector $\mathbf{v} \in \mathbb{R}^{128}$.
5. **$L_2$ Normalization**: Vector magnitude is normalized to $1.0$.
6. **Cosine Similarity Matching**: Computes similarity scores against all pre-loaded enrolled student vectors from SQLite.
7. **Threshold Decision**: Compares top similarity score against `FACE_MATCH_THRESHOLD = 0.363`:
   - $\ge 0.363 \implies$ **Recognized Student** (Green bounding box, attendance marked).
   - $< 0.363 \implies$ **Unknown Face** (Red bounding box, labeled "Unknown", ignored for attendance).

---

# 20. MATHEMATICAL EXPLANATION

### 1. Vector $L_2$ Normalization
Every 128-dimensional embedding vector $\mathbf{v} = [v_1, v_2, \dots, v_{128}]$ generated by SFace is normalized using its Euclidean ($L_2$) norm:

$$\|\mathbf{v}\|_2 = \sqrt{\sum_{i=1}^{128} v_i^2}$$

$$\hat{\mathbf{v}} = \frac{\mathbf{v}}{\|\mathbf{v}\|_2} = \left[ \frac{v_1}{\|\mathbf{v}\|_2}, \frac{v_2}{\|\mathbf{v}\|_2}, \dots, \frac{v_{128}}{\|\mathbf{v}\|_2} \right]$$

### 2. Cosine Similarity Metric
The Cosine Similarity $S_{\cos}$ between a query face vector $\mathbf{q}$ and an enrolled student vector $\mathbf{e}$ measures the cosine of the angle between them in 128-dimensional vector space:

$$S_{\cos}(\mathbf{q}, \mathbf{e}) = \frac{\mathbf{q} \cdot \mathbf{e}}{\|\mathbf{q}\|_2 \|\mathbf{e}\|_2} = \frac{\sum_{i=1}^{128} q_i \cdot e_i}{\sqrt{\sum_{i=1}^{128} q_i^2} \sqrt{\sum_{i=1}^{128} e_i^2}}$$

Since both vectors are pre-normalized to unit length ($\|\mathbf{q}\|_2 = \|\mathbf{e}\|_2 = 1.0$), Cosine Similarity simplifies directly to the vector dot product:

$$S_{\cos}(\mathbf{q}, \mathbf{e}) = \mathbf{q} \cdot \mathbf{e} = \sum_{i=1}^{128} q_i \cdot e_i$$

### 3. Recognition Threshold Decision Rule
The recognition decision is evaluated against the calibrated threshold $0.363$:

$$\text{Decision}(\mathbf{q}) = \begin{cases} \text{Student ID } k, & \text{if } \max_{k} S_{\cos}(\mathbf{q}, \mathbf{e}_k) \ge 0.363 \\ \text{Unknown Face}, & \text{if } \max_{k} S_{\cos}(\mathbf{q}, \mathbf{e}_k) < 0.363 \end{cases}$$

---

# 21. ATTENDANCE ENGINE

When an enrolled student face is recognized ($\ge 0.363$), the attendance engine executes automated attendance marking:

```text
[Recognized Face >= 0.363]
           │
           ▼
[Check 10-Second In-Memory Cooldown Map] ── (Active < 10s) ──> [Ignore Frame / Skip DB]
           │ (Cooldown Passed >= 10s)
           ▼
[Execute SQLite INSERT Statement]
           │
           ├── (First Insert Today) ──> [Record Saved: Status 'Present']
           └── (Duplicate Constraint) ──> [SQLite UNIQUE Violation Caught Safely]
```

### Protection Against Duplicate Records:
1. **In-Memory 10-Second Safety Cooldown**: An in-memory timestamp dictionary (`_cooldown_map[student_id]`) tracks the exact time of the last recognition event. Detections of the same student occurring within 10 seconds are ignored, preventing UI log flooding and redundant database hits.
2. **Database Permanent Unique Constraint**: The SQLite `attendance` table enforces `UNIQUE(student_id, attendance_date)`. If an insert attempt occurs for a student who was already marked present earlier in the day, SQLite raises a `sqlite3.IntegrityError`, which the service layer handles silently without interrupting the video stream or crashing the application.
3. **Inactive Student Handling**: Students marked `'inactive'` in the database are filtered out during model loading and will not trigger attendance even if their face is detected.

---

# 22. DATABASE DESIGN

The system uses a lightweight, serverless **SQLite 3** relational database stored locally at `data/attendance.db`.

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

### Relational Tables Summary:
1. **`schema_info`**: Tracks schema DDL version (`version INTEGER PRIMARY KEY`).
2. **`students`**: Stores profile information (`id PK`, `student_id UNIQUE`, `name`, `class_name`, `section`, `roll_number`, `phone`, `status`, `created_at`).
3. **`users`**: Stores authentication user accounts (`id PK`, `username UNIQUE`, `password_hash`, `role`, `status`).
4. **`attendance`**: Stores daily logs (`id PK`, `student_id FK`, `attendance_date`, `attendance_time`, `status`, `confidence_score`, `UNIQUE(student_id, attendance_date)`).
5. **`face_data`**: Stores enrolled 128D vectors (`id PK`, `student_id FK`, `model_identifier`, `encoding_data` JSON, `data_format`, `status`).
6. **`application_settings`**: Stores configuration key-values (`key PRIMARY KEY`, `value`, `description`).

### Transaction Safety & Security:
- **Foreign Keys Enforced**: Connection context enables `PRAGMA foreign_keys = ON;`.
- **Parameterized Queries**: All database operations use `?` parameter placeholders, completely eliminating SQL injection vulnerabilities.
- **Atomic Transactions**: Data mutations use Python context managers (`with get_db_connection():`) ensuring automatic commit on success and rollback on failure.

---

# 23. MANAGEMENT DASHBOARD

The **Management Dashboard** provides a real-time summary view of daily attendance metrics:

- **Total Registered Students**: Total count of active students enrolled in the system.
- **Present Today**: Count of students marked Present or Late for the current date.
- **Absent Today**: Calculated count of active students not marked present today ($N_{\text{absent}} = N_{\text{total}} - N_{\text{present}}$).
- **Attendance Rate %**: Percentage of active students present today ($\frac{N_{\text{present}}}{N_{\text{total}}} \times 100\%$).
- **Recent Attendance Activity Feed**: Interactive scrollable table listing recent live recognition events (Time, Student ID, Name, Class/Section, Status, Score).
- **Quick Action Buttons**: Direct navigation shortcuts to AI Attendance, Student Management, and Reports.

---

# 24. REPORTS AND EXPORT

The **Reports Module** offers searching, manual attendance status corrections, and multi-format report exports:

- **Multi-Criteria Search Filtering**: Filter attendance records by Start Date, End Date, Student Search Query (Code/Name), Class (`All`, `12`), Section (`All`, `A`), and Status (`Present`, `Absent`, `Late`, `Excused`).
- **Interactive Attendance Correction**: Authorized users (`ADMIN`) can manually adjust a student's attendance status (e.g., changing `"Absent"` to `"Excused"` with a recorded correction timestamp).
- **CSV Data Exporter**: Generates flat CSV files containing filtered attendance records.
- **OpenPyXL Excel Exporter**: Generates a styled, formatted multi-sheet Excel workbook (`.xlsx`):
  - **Sheet 1 (`"Attendance Log"`)**: Detailed log with dark-blue header formatting (`#1F497D`), bold white titles, and status cell color highlights (Green for Present, Red for Absent).
  - **Sheet 2 (`"Student Summary"`)**: Aggregated summary table listing Total Days, Present Days, Absent Days, and Overall Attendance Percentage % for every student.

---

# 25. VISUAL ANALYTICS

The **Visual Analytics Module** embeds a 2x2 grid panel of Matplotlib statistical charts rendered directly on a Tkinter canvas:

1. **Daily Attendance Trend (Top-Left Bar/Line Chart)**: Displays daily Present vs. Absent counts across selected timeframes (Past 7, 14, or 30 days).
2. **Status Distribution (Top-Right Donut Chart)**: Displays proportional percentage breakdown of Present, Absent, Late, and Excused statuses for the current date.
3. **Monthly Attendance Rate (Bottom-Left Line Chart)**: Tracks historical average attendance percentage rates across the past 6 months.
4. **Student Performance Risk Distribution (Bottom-Right Categorical Bar Chart)**: Categorizes active students into 3 exact attendance performance risk bands:
   - **Excellent (>90%)**: Attendance rate $> 90.0\%$
   - **Good (75-90%)**: Attendance rate $75.0\% \le \text{rate} \le 90.0\%$
   - **At-Risk (<75%)**: Attendance rate $< 75.0\%$

---

# 26. USER INTERFACE

The user interface is built with **CustomTkinter** adhering to a modern **dark-blue design system** (`#1F497D` primary accent, `#2ECC71` success green, `#E74C3C` error red):

- **Main Window Shell**: Unified application layout featuring topbar header, status indicators (`AI Status: MODEL AVAILABLE`), logged-in user role badge, and left navigation sidebar.
- **Left Navigation Sidebar**: Single-click tab buttons (`Dashboard`, `Students`, `AI Attendance`, `Reports`, `Analytics`) providing seamless view switching with $< 15\text{ ms}$ latency.
- **Dialogs & Modals**: Modal confirmation dialog popups prevent accidental student deactivations or logout actions.
- **Empty State Widgets**: Provides friendly feedback when search filters return zero matching database records.

---

# 27. CAMERA SYSTEM

The application provides a flexible, decoupled camera architecture built on the `FrameProvider` abstract base class:

1. **Camera Frame Provider**: Standard production provider interfacing local USB webcams or integrated laptop cameras via OpenCV `cv2.VideoCapture(index)`.
2. **Image Frame Provider**: Development/testing provider loading single static image files for deterministic AI testing.
3. **Video Frame Provider**: Testing provider reading pre-recorded video files.
4. **Mobile Camera Frame Provider**: Testing adapter connecting mobile smartphone cameras via USB tethering and DroidCam IP stream endpoints (`http://127.0.0.1:4747/video`).

*Note*: Mobile camera integration is provided for development testing purposes; primary classroom deployment uses standard USB webcams.

---

# 28. SECURITY AND PRIVACY

The system incorporates strict security and privacy protections:

- **100% Local Execution**: Zero cloud API dependencies; all facial processing and database queries execute locally on the host PC.
- **Biometric Vector Storage**: Raw camera images are **never saved to disk**. Face features are transformed into 128D mathematical float vectors. Raw photographs cannot be reconstructed from 128D vectors.
- **Parameterized SQL**: All database queries use parameterized placeholders (`?`), completely preventing SQL injection attacks.
- **PBKDF2 Password Hashing**: User authentication uses PBKDF2-HMAC-SHA256 password hashing.
- **Session Protection**: In-memory user session is completely destroyed upon logout.
- **Role-Based Authorization**: Enforces strict privilege separation between `ADMIN` and `TEACHER` accounts.

---

# 29. TESTING

The application was validated using **Pytest**, maintaining a verified test baseline of **131 passed / 0 failed tests** (100% pass rate):

### Test Category Distribution:
- **Database Tests** (20 tests): Schema creation, FK enforcement, CRUD, transactions.
- **Auth Tests** (16 tests): Password hashing, login, RBAC roles, session clearance.
- **Student Tests** (14 tests): Profile validation, unique student code checks, deactivation.
- **AI Engine Tests** (16 tests): YuNet detection, SFace 128D embeddings, Cosine threshold 0.363 matching.
- **Registration Tests** (9 tests): 5-sample capturing, quality sharpness check, vector averaging.
- **Attendance Engine Tests** (9 tests): Live pipeline, 10s cooldown, SQLite duplicate block.
- **Dashboard Tests** (5 tests): Summary metric calculations and recent activity feeds.
- **Reports & Export Tests** (9 tests): Multi-criteria search, CSV export, OpenPyXL Excel export.
- **Analytics Tests** (7 tests): Trend aggregations, donut distribution, performance bands.
- **UI Polish Tests** (5 tests): CustomTkinter view rendering and layout hierarchy.
- **Hardening Tests** (8 tests): Boundary conditions, corrupted inputs, SQL injection attempts.
- **Packaging Tests** (6 tests): PyInstaller frozen paths, `sys._MEIPASS` resolution, launcher scripts.
- **Mobile Camera Adapter Tests** (5 tests): Socket stream handling and adapter fallback.
- **Baseline Tests** (2 tests): Environment setup and dependency version checks.

---

# 30. REAL-WORLD ACCEPTANCE TEST

The packaged application executable (`dist/AIAttendanceSystem/AIAttendanceSystem.exe`) was subjected to a comprehensive 17-step clean-copy acceptance verification test:

1. **Clean-Copy Execution**: Executable launched on a fresh Windows system without Python pre-installed.
2. **First-Run Seeding**: System automatically created `data/attendance.db` and prompted for Admin account creation.
3. **Login Verification**: Admin logged in successfully; `SessionManager` established `ADMIN` privilege context.
4. **Dashboard Verification**: All 4 summary cards rendered correctly with zero initial attendance records.
5. **Student Management**: Created student profiles (`STU-101`, `STU-102`); verified unique code enforcement.
6. **Biometric Face Enrollment**: Successfully registered 5 face samples for `STU-101`; verified 128D vector saved in `face_data`.
7. **AI Recognition Stream**: Started camera feed; YuNet detected face, SFace matched `STU-101` with score `0.84 >= 0.363`; green bounding box drawn.
8. **10-Second Cooldown Verification**: Kept face in view for 30 seconds; verified only 1 attendance log entry was created.
9. **Duplicate Constraint Protection**: Attempted duplicate manual insertion for same date; verified SQLite `UNIQUE` constraint blocked insert safely.
10. **Unknown Face Rejection**: Presented unenrolled face; system drew red bounding box, labeled `"Unknown (0.24)"`, and created zero attendance logs.
11. **Reports Search & Filtering**: Applied date and class filters; verified correct records displayed in table grid.
12. **CSV Export Verification**: Exported report to CSV; verified valid text format and row counts.
13. **Excel Export Verification**: Exported report to Excel (`.xlsx`); verified OpenPyXL generated 2 formatted sheets.
14. **Visual Analytics Verification**: Opened Analytics view; verified 2x2 Matplotlib chart panel rendered all 4 visual charts.
15. **Logout & Session Destruction**: Logged out; verified session destroyed and redirected to Login screen.
16. **Offline Operation**: Disconnected all internet connections; verified 100% flawless system operation.
17. **Camera-less Fallback**: Tested system with camera disconnected; verified clean error message without crash.

---

# 31. CODE QUALITY AND HARDENING

A full 100% project repository audit was conducted across all 20 production modules.

### Summary of Audit & Refactoring Results:
- **Dead-Code Cleanup**: Removed 100% of unused imports and obsolete files; 0 dead code files remaining.
- **Tkinter Lifecycle Hardening**: Resolved 2 medium-severity Tkinter lifecycle issues:
  1. *Early CTkFont Instantiation*: Moved font creation inside active window contexts to prevent `RuntimeError: Too early to use font: no default root window`.
  2. *Window Teardown Guard*: Added `if self.winfo_exists(): self.destroy()` guards to prevent `_tkinter.TclError` during window close events.
- **Current Defect Count**: **0 Critical, 0 High, 0 Medium, 0 Low**.

---

# 32. LIMITATIONS

1. **Ambient Illumination Sensitivity**: YuNet face detection requires minimum ambient lighting. Extreme low light (under 10 lux) or direct backlighting may reduce detection confidence below $0.60$.
2. **Head Pose Boundaries**: SFace feature recognition performs optimally when head yaw and pitch remain within $\pm 30^\circ$ of frontal view. Extreme profile angles ($> 45^\circ$) lower Cosine Similarity scores.
3. **Facial Occlusions**: Heavy occlusions (full face masks, dark sunglasses covering eyes) obscure facial landmarks, preventing recognition.
4. **Single-Camera Input**: The application processes one active camera feed per running instance.
5. **CPU Latency**: Designed for low-spec CPUs, achieving 25–30 FPS at $640 \times 480$. Processing 4K video feeds on low-end CPUs may increase per-frame latency.

---

# 33. FUTURE SCOPE

While the current application completely satisfies all Class 12 CBSE Computer Science requirements, potential future extensions include:

1. **Multi-Camera RTSP IP Streaming**: Expanding the `FrameProvider` architecture to ingest multiple classroom network camera streams concurrently.
2. **Automated Guardian SMS/Email Alerts**: Integrating Twilio/SMTP APIs to send instant attendance notifications to parents.
3. **Web & Mobile Companion Client**: Developing a companion mobile dashboard app for school administrators built with FastAPI and React Native.
4. **3D Depth Anti-Spoofing**: Implementing liveness verification (eye blink or depth estimation) to prevent photo spoofing attempts.

---

# 34. ADVANTAGES

- **100% Automated**: Eliminates 5–10 minutes of manual roll call per class period.
- **Zero Cloud Costs**: Operates 100% offline without recurring cloud API fees or subscriptions.
- **Biometric Privacy**: Stores local 128D mathematical vectors; raw camera frames are discarded immediately in RAM.
- **Robust Duplicate Protection**: Combines 10-second RAM cooldown with SQLite database-level unique constraints.
- **Multi-Format Export**: Generates professional CSV and styled multi-sheet OpenPyXL Excel reports.
- **Integrated Visual Analytics**: Features embedded 2x2 Matplotlib chart panels for statistical trend analysis.

---

# 35. DISADVANTAGES

- **Lighting Dependency**: Requires adequate classroom lighting for reliable face detection.
- **Frontal View Requirement**: Students must look generally towards the camera ($\pm 30^\circ$).
- **Single Stream Limitation**: Processes one video stream per application instance.

---

# 36. APPLICATION SCREENSHOTS

*(Refer to `PROJECT_REPORT_SCREENSHOT_PLAN.md` for full visual layout specifications.)*

1. **User Login Interface**: `[SCREENSHOT PLACEHOLDER #1: User Login Screen]`
2. **First-Run Setup Window**: `[SCREENSHOT PLACEHOLDER #2: First-Run Admin Setup Window]`
3. **Management Dashboard**: `[SCREENSHOT PLACEHOLDER #3: Management Dashboard]`
4. **Student Management View**: `[SCREENSHOT PLACEHOLDER #4: Student Management Interface]`
5. **Face Registration Modal**: `[SCREENSHOT PLACEHOLDER #5: Face Biometric Registration Modal]`
6. **Real-Time AI Attendance Stream**: `[SCREENSHOT PLACEHOLDER #6: Real-Time AI Attendance Engine View]`
7. **Attendance Reports View**: `[SCREENSHOT PLACEHOLDER #7: Attendance Reports View]`
8. **Exported Excel Report**: `[SCREENSHOT PLACEHOLDER #8: Exported Excel Workbook (.xlsx) Report Output]`
9. **Visual Analytics Grid**: `[SCREENSHOT PLACEHOLDER #9: Visual Analytics 2x2 Chart Grid]`
10. **Logout Confirmation Dialog**: `[SCREENSHOT PLACEHOLDER #10: Modal Logout Confirmation Dialog]`

---

# 37. RESULTS

The **AI-Enabled Smart Attendance System** successfully fulfills all functional, architectural, security, and performance criteria:

- **Test Suite Pass Rate**: **131 passed / 0 failed (100% pass rate)** across 14 test modules.
- **AI Matching Accuracy**: Successfully recognizes enrolled faces with Cosine Similarity $\ge 0.363$ while rejecting unknown faces ($< 0.363$).
- **Duplicate Prevention**: 100% successful duplicate entry blocking via 10s RAM cooldown and SQLite `UNIQUE(student_id, attendance_date)` constraint.
- **System Performance**: View switch latency $< 15\text{ ms}$, RAM footprint $< 80\text{ MB}$, real-time CPU inference at 25–30 FPS.
- **Deployment**: Standalone PyInstaller executable folder verified on clean Windows systems.

---

# 38. CONCLUSION

The **AI-Enabled Smart Attendance System** represents a complete, robust, and privacy-conscious solution for automating classroom student attendance using artificial intelligence and computer vision.

Developed for the Senior Secondary CBSE Class 12 Computer Science curriculum, the system proves that state-of-the-art deep learning models (YuNet and SFace) can operate **100% offline on standard low-cost CPU hardware**, delivering high recognition accuracy while strictly protecting student biometric data privacy. With a 100% test pass rate across 131 automated tests, clean architecture, and standalone packaging, the project is completely ready for academic evaluation and viva voce demonstration.

---

# 39. VIVA PREPARATION

### 1. 30-Second Project Introduction
> *"Respected Examiner, my project is an **AI-Enabled Smart Attendance System** developed in Python using CustomTkinter, OpenCV, and SQLite. The system automatically detects human faces in live camera feeds using the **YuNet** neural network, extracts 128-dimensional facial feature embeddings using **SFace**, and matches them against enrolled student records using **Cosine Similarity**. It automatically marks attendance, enforces a **0.363 threshold** and **10-second cooldown**, prevents duplicate daily records via SQLite unique constraints, and provides multi-format CSV/Excel exports and visual analytics charts. The system operates **100% offline** on standard CPU hardware while keeping biometric feature data strictly local for privacy."*

### 2. 60-Second Technical Explanation
> *"Technically, the system follows a 5-tier layered architecture. When a video frame is captured by OpenCV, the **YuNet CNN detector** locates the face bounding box and 5 facial landmarks. The cropped face is aligned and passed to **SFace**, which generates an $L_2$-normalized 128-dimensional feature vector. Our decision engine computes the vector dot product (Cosine Similarity) against enrolled vectors loaded from our local **SQLite database**. If the score meets or exceeds **0.363**, the student is identified. Duplicate attendance is prevented by a **10-second in-memory cooldown map** and an enforced SQLite **`UNIQUE(student_id, attendance_date)`** database constraint. The GUI is built with **CustomTkinter**, analytics charts are rendered using **Matplotlib**, and the application is packaged with **PyInstaller** into a portable standalone Windows distribution launched via **`run_app.bat`**."*

### 3. Key Viva Questions & Answers
- **Q1: Why use YuNet and SFace instead of basic Haar Cascades?**
  - *A: Haar Cascades rely on simple edge/line pixel intensity differences and fail under varying lighting or head angles. YuNet and SFace are deep convolutional neural networks (CNNs) trained on millions of faces, extracting invariant 128D facial features.*
- **Q2: How does the system protect biometric privacy?**
  - *A: Raw camera images are processed in RAM and discarded immediately. Biometrics are stored strictly as 128D mathematical vectors in local SQLite. Original facial photographs cannot be reconstructed from 128D vectors.*
- **Q3: What is the significance of threshold 0.363?**
  - *A: 0.363 is the official Cosine Similarity threshold for OpenCV SFace. Scores $\ge 0.363$ indicate high feature similarity (Recognized Student), while scores $< 0.363$ represent distinct individuals (Unknown Face).*
- **Q4: Why use SQLite instead of MySQL?**
  - *A: SQLite is local, serverless, single-file (`attendance.db`), zero-configuration, and requires no external background database server, making it ideal for offline desktop applications.*

---

# 40. REFERENCES

1. **Python Software Foundation**: Python 3.13.14 Documentation.
2. **OpenCV DNN Module**: Open Source Computer Vision Library & OpenCV Zoo. ONNX Models: YuNet (`face_detection_yunet_2023mar.onnx`) & SFace (`face_recognition_sface_2021dec.onnx`).
3. **CustomTkinter GUI Library**: Modern Dark-Themed Tkinter UI Framework by Tom Schimansky.
4. **SQLite Database Consortium**: SQLite 3 Self-Contained Relational Database Engine.
5. **Matplotlib Development Team**: Matplotlib 2D Plotting Library for Python & Tkinter Integration (`FigureCanvasTkAgg`).
6. **OpenPyXL Project**: OpenPyXL — Python Library to Read/Write Excel 2010 xlsx/xlsm Files.
7. **Pandas Project**: Pandas Data Analysis and Manipulation Tool.
8. **PyInstaller Development Team**: PyInstaller Standalone Application Freezer.
9. **Pytest Development Team**: Pytest Framework for Python Testing.
10. **Central Board of Secondary Education (CBSE)**: Senior Secondary Computer Science (Code 083) Curriculum & Project Evaluation Guidelines.
