# Stage 12 Implementation Plan — Packaging & Distribution

## Objective

Build Stage 12 of the AI-Enabled Smart Attendance System: Packaging & Distribution. Create a standalone, self-contained, portable Windows application package enabling effortless demonstration, single-click deployment, and first-run environment initialization without requiring pre-installed Python, PyPI packages, GPU drivers, or internet connectivity.

---

## Master Requirements

From Stage 12 of `AI_Attendance_System_Master_Requirements.md`:
1. **Dependency Verification**: Confirm all required runtime libraries (`customtkinter`, `opencv-python`, `openpyxl`, `matplotlib`, `pillow`, `numpy`, `sqlite3`) are bundled.
2. **Application Packaging**: Package application using PyInstaller / standalone executable build specification (`build_app.py` / `ai_attendance_system.spec`).
3. **Model-File Handling**: Ensure offline ONNX models (`models/yunet.onnx`, `models/face_recognition_sface_2021dec.onnx`) are bundled and unpacked to the execution directory.
4. **Data-Directory Handling**: Auto-create runtime directories (`data/`, `data/face_data/`, `logs/`) on first boot if missing.
5. **First-Run Setup**: Initialize SQLite database (`attendance.db`), create default admin account setup prompt on first launch.
6. **Clean Windows Environment Validation**: Ensure 100% offline, CPU-first, low-resource deployment on target machine (Intel Core i3-12100 CPU, 12 GB RAM, Intel UHD 730 Graphics, Windows 10/11).

---

## Required Features

1. **PyInstaller Build Script & Spec (`build_app.py`, `ai_attendance_system.spec`)**:
   - Compiles entry point `app/main.py` into a standalone Windows executable (`dist/AIAttendanceSystem/AIAttendanceSystem.exe`).
   - Bundles required ONNX AI models (`models/yunet.onnx`, `models/face_recognition_sface_2021dec.onnx`).
   - Bundles CustomTkinter theme assets, fonts, and Matplotlib data files.
2. **Standalone Launcher & Distribution Bundle (`run_app.bat` / Portable Distribution Zip)**:
   - Provides a single-click Windows batch launcher script (`run_app.bat`) for easy evaluation.
3. **First-Run Environment Auto-Initialization**:
   - Automatically detects missing database or model files on first launch and initializes them cleanly.
4. **Standalone Packaging Verification Suite (`tests/test_stage12_packaging.py`)**:
   - Automated tests verifying packaging manifests, path resolution helpers (`sys._MEIPASS`), model file bundlers, and first-run setup hooks.

---

## Acceptance Criteria

- [ ] Complete PyInstaller build script (`build_app.py`) created.
- [ ] Standalone executable specification (`ai_attendance_system.spec`) created.
- [ ] ONNX model files (`yunet.onnx`, `face_recognition_sface_2021dec.onnx`) successfully bundled in data manifest.
- [ ] Automated directory creation (`data/`, `data/face_data/`, `logs/`) verified on first run.
- [ ] Portable launcher script (`run_app.bat`) created for non-technical evaluators.
- [ ] Application operates 100% offline without requiring internet or GPU.
- [ ] All 125 existing tests + Stage 12 packaging tests pass cleanly (130+ tests).

---

## Existing Components Reused

- `app/config.py`: Path resolution (`BASE_DIR`, `MODELS_DIR`, `DATABASE_PATH`, `FACE_DATA_DIR`).
- `app/main.py`: Entry point and `verify_environment()` runtime inspector.
- `app/database/`: `initialize_database()` and schema definitions.
- `app/ai/models/`: `yunet.onnx` and `face_recognition_sface_2021dec.onnx`.
- `app/ui/`: `MainWindow`, `LoginWindow`, `DashboardViewFrame`, `ReportsViewFrame`, `AnalyticsViewFrame`.

---

## New Components

- **`build_app.py`**: Automated PyInstaller packaging & distribution script.
- **`ai_attendance_system.spec`**: PyInstaller asset bundling specification file.
- **`run_app.bat`**: Single-click batch launcher script.
- **`tests/test_stage12_packaging.py`**: Automated test suite for packaging & manifest path resolution.
- **`docs/STAGE_12_IMPLEMENTATION_PLAN.md`**: This implementation plan document.
- **`docs/STAGE_12_REPORT.md`**: Executive summary report for Stage 12.
- **`docs/PACKAGING.md`**: Distribution & packaging user guide.

---

## Database Changes

- **No Schema Changes Required**.
- Auto-initializes SQLite database (`data/attendance.db`) on first launch if not present.

---

## AI Integration

- Bundles YuNet (`yunet.onnx`) and SFace (`face_recognition_sface_2021dec.onnx`) directly within the build package.
- Runtime path helper resolves relative model locations in both script mode and PyInstaller frozen mode (`sys._MEIPASS`).

---

## Authentication / RBAC

- Preserves full RBAC security (`admin` / `teacher`). First-run setup guides default admin account creation.

---

## UI

- CustomTkinter UI framework bundled with dark-blue theme assets. Window title, sidebar icons, and Matplotlib canvas render cleanly in frozen executable mode.

---

## Attendance Integration

- Reuses existing attendance pipeline, 10s cooldown, and per-day duplicate protection.

---

## Dashboard Integration

- Reuses existing management dashboard summary stat cards and activity feed.

---

## Reporting Integration

- Reuses existing search filters, CSV exporter, and OpenPyXL Excel exporter.

---

## Analytics Integration

- Reuses existing 4 Matplotlib chart panels with `FigureCanvasTkAgg` canvas embedding in frozen executable mode.

---

## Security

- **Local Storage Only**: Database and face embeddings stay on local disk (`data/`).
- **Zero Cloud / Zero Network**: Application makes zero HTTP requests and requires zero cloud APIs.
- **Biometric Privacy**: Embeddings remain stored inside local SQLite database; raw face photos are discarded immediately after processing.

---

## Performance

- **Target PC**: Intel Core i3-12100 CPU, 12 GB RAM, Intel UHD 730 Integrated Graphics, Windows 10/11.
- **Executable Startup Time**: < 3.0 seconds.
- **Resource Footprint**: < 80 MB RAM in standalone frozen mode.

---

## Deployment

- Package output folder: `dist/AIAttendanceSystem/`.
- Portable distribution archive: `dist/AIAttendanceSystem_Portable.zip`.
- Fully portable — can be copied to any USB drive or Windows PC and launched immediately.

---

## Packaging

- Built via PyInstaller:
  ```powershell
  python build_app.py
  ```
- Spec handles binary inclusion for OpenCV DLLs, CustomTkinter themes, and ONNX model files.

---

## Testing

- New test suite in `tests/test_stage12_packaging.py`:
  - Test PyInstaller path resolution helper (`get_resource_path()`).
  - Test ONNX model file presence in package manifest.
  - Test data directory auto-creation on missing path.
  - Test database auto-initialization on first run.

---

## Documentation

- `docs/STAGE_12_IMPLEMENTATION_PLAN.md` (this plan)
- `docs/STAGE_12_REPORT.md`
- `docs/PACKAGING.md`
- `docs/PROJECT_CHECKPOINT.md` (updated to Stage 12 Complete)

---

## Academic Presentation

- The portable package allows the student to plug in a USB drive into any examination PC or presentation laptop and launch `run_app.bat` instantly without installing Python or dependencies.

---

## Implementation Substages

- **11A**: Create PyInstaller specification (`ai_attendance_system.spec`) and automated build script (`build_app.py`).
- **11B**: Implement launcher batch script (`run_app.bat`) and first-run directory auto-creation hooks.
- **11C**: Create packaging automated test suite (`tests/test_stage12_packaging.py`).
- **11D**: Execute build & run regression tests (130+ tests passing).
- **11E**: Generate Stage 12 documentation and Git checkpoint.

---

## Exit Criteria

- [ ] `build_app.py` script executes cleanly and creates `dist/AIAttendanceSystem/`.
- [ ] Model files (`yunet.onnx` & `sface.onnx`) bundled and accessible at runtime.
- [ ] `run_app.bat` launches application cleanly.
- [ ] Database and data directories auto-create on first run.
- [ ] All 125 existing tests + Stage 12 packaging tests pass cleanly.
- [ ] Git working tree clean, commit created, Stage 13 awaiting approval.

---

## Risks

- **OpenCV / CustomTkinter DLL Bundling**: Resolved via explicit `--add-data` flags in PyInstaller build script.

---

## Rollback Strategy

If any regression occurs during Stage 12 development, revert to git commit `cf7cde4` (`stage-11: harden system and expand test coverage`).
