# Stage 6 Implementation Plan — AI Attendance Engine & Real-Time Recognition

## Objective
Build Stage 6 of the AI-Enabled Smart Attendance System: an automated AI attendance engine and real-time/offline recognition interface. Connect the Stage 4 AI recognition pipeline (`AIRecognitionPipeline`, YuNet, SFace, Cosine Matcher) and Stage 5 face registration embeddings with the Stage 1 SQLite attendance database (`attendance` table) through a dedicated CustomTkinter Attendance View UI, backend service layer, duplicate attendance protection, cooldown management, and camera-less file provider fallback.

---

## Master Requirements
From Section 3.4, 3.5 & Stage 6 of `AI_Attendance_System_Master_Requirements.md`:
1. **Real-time / Frame Recognition**: Access webcam or image/video file stream, detect faces, extract SFace 128D embeddings, compare against enrolled students in local SQLite DB using Cosine Similarity ($\ge 0.363$).
2. **Automatic Attendance Creation**: When a registered student is recognized with sufficient confidence ($\ge 0.363$), automatically create a `Present` attendance record for today's date (`YYYY-MM-DD`), current time (`HH:MM:SS`), and status (`Present`).
3. **Duplicate Prevention**: Enforce rule of max 1 automatic `Present` record per student per date. Re-recognizing the same student on the same day must not create duplicate records.
4. **Recognition Feedback & UI**: Display live video/image frame with visual bounding box overlays (Green for recognized student with name and confidence score, Red for unknown face). Show live attendance event activity feed log.
5. **Unknown Face Rejection**: Unknown or un-enrolled faces are rejected and logged as `Unknown Face` without creating attendance records.
6. **Inactive Student Protection**: Inactive student records are blocked from receiving attendance records.
7. **Camera-less Provider Support**: Support `ImageFrameProvider` and `VideoFrameProvider` for testing without webcams, alongside `CameraFrameProvider` with graceful missing-hardware error displays.
8. **RBAC & Authorization**: Enforce active user session requirements (`SessionManager`) at backend service layer.

---

## Required Features

1. **Attendance Service Layer (`app/attendance/service.py`)**:
   - `process_recognition_frame(frame, mark_attendance=True, db_path=None)`: processes frame, identifies faces, marks attendance for recognized active students, and returns annotated frame with bounding boxes.
   - `get_today_attendance_summary(db_path=None)`: queries today's total present count, total registered students, and attendance percentage.
   - `record_manual_attendance(student_id, date_str, time_str, status, db_path=None)`: authorized manual attendance override.
2. **CustomTkinter Attendance View (`app/ui/attendance.py`)**:
   - Live stream canvas displaying annotated frames with bounding box overlays.
   - Provider selection controls (USB Webcam, Test Video File, Test Image File).
   - Real-time recognition event log feed panel ("10:15:32 — Present: Jane Smith [STU-102] (Conf: 0.88)").
   - Quick statistics counter ("Present Today: 12", "Unknown Hits: 2").
   - Start / Stop recognition stream controls.
3. **Integration with Main Application Layout (`app/ui/main_window.py`)**:
   - Dedicated "AI Attendance Camera" tab in top-level CustomTkinter window navigation.
4. **Automated Test Suite (`tests/test_stage6_attendance.py`)**:
   - Complete automated unit and integration tests covering attendance marking, duplicate prevention, cooldown protection, unknown face handling, inactive student protection, RBAC checks, and provider integration.

---

## Existing Components Reused
- `app/database/`: `create_attendance`, `check_duplicate_attendance`, `get_attendance_by_date`, `list_recent_attendance`, `get_student_by_id`.
- `app/auth/`: `get_session()`, `SessionManager` (session validation and RBAC).
- `app/ai/`: `AIRecognitionPipeline`, `YuNetFaceDetector`, `SFaceRecognizer`, `FaceMatcher`, `FrameProvider` hierarchy (`ImageFrameProvider`, `VideoFrameProvider`, `CameraFrameProvider`).
- `app/students/`: `list_all_students()`, `get_student_detail()`.

---

## New Components
- **`app/attendance/service.py`**: High-level Attendance Engine Service module handling automatic recognition, duplicate validation, cooldown tracking, and manual record entry under RBAC.
- **`app/ui/attendance.py`**: Dedicated CustomTkinter Attendance View tab/frame with live stream canvas, visual bounding box overlay rendering, real-time activity log feed, provider switcher, and AI status indicators.
- **`tests/test_stage6_attendance.py`**: Dedicated automated test suite for Stage 6 AI Attendance Engine.

---

## Database Changes
- **No Schema Changes Required**.
- Uses existing Stage 1 SQLite `attendance` table:
  ```sql
  CREATE TABLE IF NOT EXISTS attendance (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER NOT NULL,
      attendance_date TEXT NOT NULL,
      attendance_time TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'Present',
      recognition_method TEXT NOT NULL DEFAULT 'automatic',
      confidence_score REAL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
      UNIQUE (student_id, attendance_date)
  );
  ```

---

## AI Integration
- Reuses loaded `AIRecognitionPipeline` (YuNet face detector + SFace feature embedder + Cosine matcher).
- Processes frames in real-time or batch static mode.
- Renders green bounding boxes with `Student Name (Similarity Score)` for matches $\ge 0.363$.
- Renders red bounding boxes with `Unknown (Similarity Score)` for matches $< 0.363$.

---

## Authentication/RBAC
- Backend service methods (`process_recognition_frame`, `record_manual_attendance`) require an active authenticated user session (`SessionManager`). Unauthenticated requests throw `PermissionError`.

---

## UI
- `AttendanceViewFrame` (`app/ui/attendance.py`) integrated into top-level navigation.
- Camera / Video / Image provider switcher.
- Live canvas displaying frame with colored bounding boxes.
- Activity feed list box displaying timestamped attendance logs.

---

## Security
- **Local Database Storage**: All attendance records persisted in local SQLite database (`data/attendance.db`).
- **No Cloud Transmission**: 100% offline, zero network API calls.
- **Parameterized SQL**: All database operations use parameterized bindings (`?`).
- **Zero Raw Image Retention**: Frames processed in RAM and discarded immediately after rendering.

---

## Performance
- Target System: Intel Core i3-12100 CPU, 12 GB RAM, Integrated Intel UHD 730, Windows 10.
- Detection Latency: ~3.8 ms per frame.
- Embedding & Matching Latency: ~25.1 ms per face.
- Target FPS: 15–30 FPS on CPU.
- Cooldown Window: 10 seconds in-memory cooldown per student ID prevents repeated DB query spam.

---

## Testing
- Automated test suite in `tests/test_stage6_attendance.py`:
  - Service layer RBAC authorization check
  - Automatic attendance record creation for recognized student
  - Duplicate attendance restriction (1 record per student per date)
  - 10-second cooldown protection
  - Unknown face rejection (no attendance created)
  - Inactive student protection (no attendance created for deactivated student)
  - Multi-face recognition handling in single frame
  - Camera unavailable graceful error display
  - Image and Video provider recognition workflow
  - Parameterized SQL safety and database integration

---

## Documentation
- `docs/STAGE_6_IMPLEMENTATION_PLAN.md` (this plan)
- `docs/STAGE_6_IMPLEMENTATION.md`
- `docs/STAGE_6_TESTING.md`
- `docs/STAGE_6_REPORT.md`

---

## Implementation Substages
- **6A**: Attendance Service Layer (`app/attendance/service.py`) connecting AI Recognition Pipeline with Database Attendance Repository and RBAC.
- **6B**: CustomTkinter Attendance View UI (`app/ui/attendance.py`) with frame canvas, bounding box overlays, activity feed, and provider switcher.
- **6C**: Main Application Window Layout Integration (`app/ui/main_window.py` / `app/ui/`) adding the "AI Attendance Engine" view tab.
- **6D**: Comprehensive Automated Test Suite (`tests/test_stage6_attendance.py`) & Documentation.

---

## Exit Criteria
- [ ] Registered and enrolled student recognized in frame $\rightarrow$ `Present` record created for today.
- [ ] Duplicate recognition on same date does NOT create duplicate DB entries.
- [ ] Unknown faces rejected without creating attendance records.
- [ ] Inactive students blocked from receiving attendance.
- [ ] Live canvas renders green bounding boxes for known students and red for unknown faces.
- [ ] UI activity log feed displays real-time attendance events.
- [ ] Camera absence handled gracefully with fallback to Image/Video mode.
- [ ] RBAC authorization enforced at service layer.
- [ ] All existing (77) and new Stage 6 tests pass (target: 90+ tests).
- [ ] Production application launches without errors (`main.py`).
- [ ] Working tree clean, zero secrets/biometric photos committed, Git checkpoint created.

---

## Risks
- **No Physical Camera on Dev Machine**: Mitigated by full `ImageFrameProvider` and `VideoFrameProvider` support for recognition testing and camera-less graceful fallback.
- **High CPU Usage on Continuous Video Streams**: Mitigated by configurable frame sampling interval (e.g. process 1 frame every 100 ms) and 10s recognition cooldown.

---

## Rollback Strategy
If any regression occurs during Stage 6 development, revert to git commit `8316c73` (`stage-5: implement face registration`).
