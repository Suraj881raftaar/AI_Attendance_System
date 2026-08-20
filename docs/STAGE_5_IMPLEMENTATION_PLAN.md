# Stage 5 Implementation Plan — Student Face Registration (Enrollment) System

## Objective
Connect student records with AI face data through a comprehensive, dedicated Face Registration & Biometric Management System. Provide complete UI and backend service workflows for face sample acquisition (supporting static images, video, and USB webcam streams), real-time quality validation (size, count, sharpness), multi-sample embedding averaging, database storage, re-enrollment, and face data deletion/deactivation under RBAC authorization.

---

## Requirements
From Section 3.3 & Stage 5 of `AI_Attendance_System_Master_Requirements.md`:
1. **Frame Capture & Provider Support**: Capture face frames through camera hardware or camera-less file providers (`ImageFrameProvider`, `VideoFrameProvider`, `CameraFrameProvider`).
2. **Real-time Quality Checks**:
   - Verify single face present (reject zero or multiple faces).
   - Verify minimum face size ($\ge 60 \times 60$ pixels).
   - Verify image sharpness (Laplacian variance $\ge 25.0$).
3. **Multi-Sample Capture & Averaging**: Capture 5 distinct face samples, generate 128D feature embeddings via SFace, compute L2-normalized mean feature vector, and serialize as JSON string.
4. **Database Association**: Save face representation in SQLite `face_data` table linked to `student_id` with `model_identifier='opencv_sface_v1'`.
5. **Student Status & UI Integration**: Update student face registration status badge (`Enrolled` vs `Pending`) in Student Management UI.
6. **Re-Registration & De-Registration**: Allow authorized users to overwrite/update existing face registration or deactivate/delete face data.
7. **RBAC & Authorization**: Enforce authenticated session checks for all face enrollment and deletion endpoints.
8. **Camera-less Support**: Graceful camera absence detection and fallback to file mode.

---

## Existing Components Used
- `app/database/`: SQLite connection, `face_data` repository (`create_or_update_face_data`, `get_face_data_by_student`, `deactivate_face_data`), `students` repository (`get_student_by_id`).
- `app/auth/`: `get_session()`, `SessionManager` (RBAC session validation).
- `app/ai/`: `YuNetFaceDetector` (`detector.py`), `SFaceRecognizer` (`embedder.py`), `FaceEnrollmentManager` (`enrollment.py`), `FrameProvider` hierarchy (`providers/`).
- `app/ui/`: `StudentManagementFrame` (`app/ui/students.py`), CustomTkinter dialog components.

---

## New Components Required
- **`app/students/registration.py`**: High-level Student Face Registration service module connecting Student Service layer with AI Enrollment Manager and enforcing business logic / RBAC boundaries.
- **`app/ui/registration_view.py`**: Dedicated, interactive CustomTkinter Face Registration modal dialog/view with live camera/image frame preview, real-time sample quality indicators, progress bar (0/5 samples captured), re-registration confirmation, and clear user feedback messages.
- **`tests/test_stage5_registration.py`**: Dedicated automated test suite covering full registration workflow, sample quality validation, multi-sample averaging, re-registration, face data deletion, RBAC authorization, and UI component instantiation.

---

## Database Changes
- **No Schema Changes Required**.
- Uses existing Stage 1 SQLite `face_data` table:
  ```sql
  CREATE TABLE IF NOT EXISTS face_data (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER NOT NULL,
      model_identifier TEXT NOT NULL,
      encoding_data TEXT NOT NULL,
      data_format TEXT NOT NULL DEFAULT 'json',
      status TEXT NOT NULL DEFAULT 'active',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
  );
  ```

---

## UI Changes
- Update `StudentManagementFrame` table to display explicit face enrollment status badges (`Enrolled` in green, `Pending` in orange) and a dedicated "Enroll Face" action button per active student row.
- Create `FaceRegistrationDialog` (`app/ui/registration_view.py`) with:
  - Live capture mode selector (Image File, Video File, USB Webcam).
  - Sample capture progress indicator (e.g. "Samples Captured: 3 / 5").
  - Quality feedback label ("Face Detected (130x130 px) - Sharpness OK").
  - Re-enrollment warning confirmation dialog.
  - Delete/Remove Face Data option for enrolled students.

---

## Authentication/RBAC
- All face registration, re-registration, and face-data deactivation operations require an authenticated active user session (`SessionManager`).
- Unauthenticated requests trigger `PermissionError` at both service and UI layers.

---

## AI Integration
- Consumes `YuNetFaceDetector` for real-time face bounding box and quality check.
- Consumes `SFaceRecognizer` for 128D feature extraction and L2 normalization.
- Uses `FaceEnrollmentManager` for sample validation and mean vector computation.

---

## Security
- **Local Storage Only**: All feature vectors remain in local SQLite.
- **Zero Raw Image Retention**: Images processed in memory (RAM) and discarded. Zero photo files stored to disk or committed to Git repository.
- **No Network / External API**: 100% offline local processing.
- **Parameterized SQL**: All database operations use parameterized bindings.

---

## Performance
- Target System: Intel Core i3-12100, 12 GB RAM, Integrated Intel UHD 730, Windows, CPU-first.
- Sample Capture & Quality Check Latency: < 15 ms per frame.
- Embedding Generation & Averaging Latency: < 30 ms for 5 samples.
- Memory Footprint: < 5 MB additional RAM overhead during registration.

---

## Testing
- Automated test coverage in `tests/test_stage5_registration.py`:
  - Student registration service authorization (RBAC)
  - Single face vs multi-face vs no-face sample filtering
  - Face size and sharpness quality validation thresholds
  - 5-sample vector averaging and L2 normalization accuracy
  - Database persistence and retrieval verification
  - Re-registration overwriting existing active face data
  - Face data deletion/deactivation
  - Camera absence graceful handling

---

## Documentation
- `docs/STAGE_5_IMPLEMENTATION_PLAN.md` (this document)
- `docs/STAGE_5_IMPLEMENTATION.md`
- `docs/STAGE_5_TESTING.md`
- `docs/STAGE_5_REPORT.md`

---

## Implementation Substages
- **5A**: Student Registration Service Layer (`app/students/registration.py`) connecting RBAC, Student Management, and `FaceEnrollmentManager`.
- **5B**: Interactive Face Registration UI View (`app/ui/registration_view.py`) with multi-sample progress, quality feedback, and provider selection.
- **5C**: UI Integration in Student Management View (`app/ui/students.py`) with face data status badges and enrollment action buttons.
- **5D**: Comprehensive Automated Test Suite (`tests/test_stage5_registration.py`) & Documentation.

---

## Exit Criteria
- [ ] Registered students can be enrolled with 5 face samples using image/video/camera providers.
- [ ] Real-time quality checks reject multi-face, undersized, or blurry frames.
- [ ] 128D mean feature vector is computed, normalized, and saved to SQLite `face_data`.
- [ ] Student management UI displays accurate face registration status badges (`Enrolled` / `Pending`).
- [ ] Re-registration overwrites previous face data cleanly.
- [ ] Face data deletion/deactivation works.
- [ ] Camera absence is handled gracefully without crashing.
- [ ] Session RBAC permission checks enforced.
- [ ] All existing (68) and new Stage 5 tests pass (target: 80+ tests).
- [ ] Production application launches without errors.
- [ ] Working tree clean, zero secrets/biometric photos committed, Git checkpoint created.

---

## Risks
- **No Physical Camera on Dev Machine**: Mitigated by full `ImageFrameProvider` and `VideoFrameProvider` support for sample collection and camera absence graceful fallback.
- **Poor Image Quality**: Mitigated by strict size ($\ge 60 \times 60$) and Laplacian variance sharpness checks.

---

## Rollback Strategy
If any regression occurs during Stage 5 development, revert to git commit `4090e02` (`stage-4: implement offline face recognition`).
