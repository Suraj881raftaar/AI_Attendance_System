# Technical Architecture Specification

## 1. Architectural Philosophy

The AI-Enabled Smart Attendance System is designed following a **Layered Architecture** with clean separation of concerns across 5 primary boundaries:

```text
+-----------------------------------------------------------------------+
| UI PRESENTATION LAYER (CustomTkinter Views & MainWindow Shell)        |
+-----------------------------------------------------------------------+
| APPLICATION SERVICE LAYER (Auth, Students, Attendance, Reports, etc.) |
+-----------------------------------------------------------------------+
| AI ENGINE & COMPUTER VISION (YuNet, SFace, Matcher, Frame Providers)  |
+-----------------------------------------------------------------------+
| REPOSITORY DATA ACCESS LAYER (Parameterized SQL & Transactions)        |
+-----------------------------------------------------------------------+
| PERSISTENCE LAYER (Local SQLite Database `data/attendance.db`)        |
+-----------------------------------------------------------------------+
```

---

## 2. Decoupled Service Modules

1. **`app.config`**: Centralized configuration, application constants, path resolution (`get_resource_path()`), PyInstaller `sys._MEIPASS` detection, and directory initialization.
2. **`app.database`**: Low-level SQLite database repository containing schema creation, foreign key enforcement, transaction wrappers, parameterized queries, and CRUD functions.
3. **`app.auth`**: User authentication, password hashing (`pbkdf2:sha256`), RBAC authorization (`admin`, `teacher`), and thread-safe session manager (`SessionManager`).
4. **`app.students`**: Student lifecycle management, detail updates, deactivations, and face biometric sample registration.
5. **`app.ai`**: Modular computer vision pipeline:
   - `FrameProvider`: Abstract frame provider with implementations `CameraFrameProvider`, `ImageFrameProvider`, `VideoFrameProvider`, `MobileCameraAdapter`.
   - `YuNetFaceDetector`: OpenCV DNN YuNet face detection wrapper (`yunet.onnx`).
   - `SFaceRecognizer`: OpenCV DNN SFace feature embedding extractor (`sface_2021dec.onnx`).
   - `FaceMatcher`: Cosine similarity feature matcher ($\ge 0.363$) against active enrolled student database records.
   - `AIRecognitionPipeline`: High-level orchestrator coordinating frame processing, detection, embedding, matching, 10s cooldown, and attendance insertion.
6. **`app.attendance`**: Attendance service managing real-time processing and manual attendance corrections.
7. **`app.dashboard`**: Summary metrics aggregation (`total_students`, `present_today`, `absent_today`, `attendance_percentage`).
8. **`app.reports`**: Multi-criteria search filtering, student attendance summaries, CSV exporter, and OpenPyXL Excel workbook exporter.
9. **`app.analytics`**: Statistical aggregations (daily trend, status distribution, monthly trend, performance categorization) and Matplotlib figure renderer (`chart_renderer.py`).
10. **`app.ui`**: CustomTkinter graphical interface (`MainWindow`, `LoginWindow`, `DashboardViewFrame`, `StudentManagementFrame`, `AttendanceViewFrame`, `ReportsViewFrame`, `AnalyticsViewFrame`, `ConfirmationDialog`, `EmptyStateWidget`).

---

## 3. Data Flow Diagram

```text
[Camera/Video Stream] -> [FrameProvider] -> [YuNet Detector] (Bounding Box)
                                                    ↓
[Database Enrolled Embeddings] -> [FaceMatcher] <- [SFace Embedder] (128D Vector)
                                       ↓ (Score >= 0.363 & 10s Cooldown)
                         [SQLite Database Insertion]
                                       ↓
                       [Dashboard & Reports UI Refresh]
```
