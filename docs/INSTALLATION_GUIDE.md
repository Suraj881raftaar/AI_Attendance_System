# Installation & Setup Guide

## 1. System Requirements

- **Operating System**: Microsoft Windows 10 or 11 (64-bit)
- **Processor**: Intel Core i3-12100 CPU @ 3.30GHz (or equivalent dual-core x86_64 CPU)
- **Memory (RAM)**: 4 GB minimum (12 GB recommended)
- **Graphics (GPU)**: Integrated Intel UHD 730 Graphics (No dedicated GPU or NVIDIA CUDA required)
- **Network**: **100% Offline** (Zero internet connection required after initial setup)
- **Camera (Optional)**: USB Webcam, Integrated Laptop Web Camera, or Mobile Camera Test Adapter (DroidCam via USB tethering). Application includes built-in Image and Video file testing providers if no physical camera is connected.

---

## 2. Option A: Running Standalone Executable (Recommended for Evaluators)

No Python installation or dependency setup is required.

1. Open the project root directory `C:\SURAJ\AI_Attendance_System\` or the distribution folder `dist\AIAttendanceSystem\`.
2. Double-click **`run_app.bat`** (or `AIAttendanceSystem.exe`).
3. On first run, the system automatically creates the runtime data folders (`data/`, `data/face_data/`, `logs/`) and initializes the SQLite database (`data/attendance.db`).
4. Create the initial Administrator account when prompted.

---

## 3. Option B: Running from Source in Python Development Mode

### Prerequisites:
- Python 3.13.x (64-bit) installed and added to `PATH`.

### Step-by-Step Setup:

1. **Open Terminal / Command Prompt** in project root directory:
   ```cmd
   cd C:\SURAJ\AI_Attendance_System
   ```

2. **Create and Activate Virtual Environment**:
   ```cmd
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Required Packages**:
   ```cmd
   pip install -r requirements.txt
   ```

4. **Verify Environment Setup**:
   ```cmd
   python -m app.main --cli-only
   ```

5. **Launch Desktop Application GUI**:
   ```cmd
   python -m app.main
   ```

---

## 4. Running Automated Tests

To execute the complete 131-test automated suite:
```cmd
.\venv\Scripts\python.exe -m pytest tests/
```

Expected Output: `131 passed in ~13 seconds`

---

## 5. Compiling Standalone Executable Build

To compile a new standalone PyInstaller executable package:
```cmd
python build_app.py
```
Output executable: `dist/AIAttendanceSystem/AIAttendanceSystem.exe`
