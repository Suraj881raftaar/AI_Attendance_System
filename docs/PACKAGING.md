# Standalone Packaging & Distribution Guide

## 1. Executive Summary

Stage 12 delivers a standalone, self-contained Windows application distribution of the AI-Enabled Smart Attendance System (`dist/AIAttendanceSystem/`).

The packaged application requires **NO pre-installed Python runtime, NO pip packages, NO internet connectivity, NO GPU/CUDA hardware**, and **NO administrative privileges**.

---

## 2. Distribution Package Structure

```text
dist/AIAttendanceSystem/
│
├── AIAttendanceSystem.exe        # Main standalone Windows binary
├── run_app.bat                   # Portable single-click batch launcher
│
└── _internal/                    # Bundled Python DLLs & Read-only assets
    ├── models/
    │   ├── face_detection/
    │   │   └── face_detection_yunet_2023mar.onnx
    │   └── face_recognition/
    │       └── face_recognition_sface_2021dec.onnx
    ├── customtkinter/              # Bundled CustomTkinter dark-blue theme assets
    ├── matplotlib/                 # Bundled Matplotlib chart renderer data
    └── ... (OpenCV, PIL, SQLite DLLs)
```

---

## 3. How to Demonstrate / Evaluate the Application

### Method A: Single-Click Launcher (Recommended for Evaluators)
1. Double-click `run_app.bat` inside `dist/AIAttendanceSystem/` (or in the project root directory).
2. The application opens directly to the GUI Login Window.

### Method B: Direct Executable Launch
1. Double-click `AIAttendanceSystem.exe` in `dist/AIAttendanceSystem/`.

---

## 4. Runtime Writable Data Directories

On first boot, the application automatically creates the following writable directories in the executable's folder:

- `data/`: Holds the local SQLite database (`attendance.db`).
- `data/face_data/`: Holds encrypted/enrolled student face vector metadata.
- `logs/`: Holds runtime application log outputs.

> [!IMPORTANT]
> User data, registered students, and attendance records persist in `data/attendance.db` when the application is closed and reopened. The database is **NEVER** reset automatically upon launch.
