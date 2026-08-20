"""
Automated Build & Packaging Script for AI-Enabled Smart Attendance System.
Compiles entry point into standalone Windows executable using PyInstaller.
"""

import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
SPEC_FILE = BASE_DIR / "ai_attendance_system.spec"


def create_bat_launcher(target_dir: Path):
    """Create portable single-click Windows batch launcher script."""
    bat_content = (
        "@echo off\r\n"
        "title AI-Enabled Smart Attendance System\r\n"
        "echo Launching AI-Enabled Smart Attendance System...\r\n"
        'set "APP_DIR=%~dp0"\r\n'
        'if exist "%APP_DIR%AIAttendanceSystem.exe" (\r\n'
        '    start "" "%APP_DIR%AIAttendanceSystem.exe"\r\n'
        ") else if exist \"%APP_DIR%dist\\AIAttendanceSystem\\AIAttendanceSystem.exe\" (\r\n"
        '    start "" "%APP_DIR%dist\\AIAttendanceSystem\\AIAttendanceSystem.exe"\r\n'
        ") else (\r\n"
        "    echo Error: AIAttendanceSystem.exe not found.\r\n"
        "    pause\r\n"
        ")\r\n"
    )
    launcher_path = target_dir / "run_app.bat"
    launcher_path.write_text(bat_content, encoding="utf-8")
    print(f"[PACKAGING] Created launcher: {launcher_path}")


def main():
    print("=" * 60)
    print("  AI-Enabled Smart Attendance System — Packaging System")
    print("=" * 60)

    # 1. Clean previous build artifacts
    if BUILD_DIR.exists():
        print("[CLEAN] Removing previous build directory...")
        shutil.rmtree(BUILD_DIR, ignore_errors=True)

    if DIST_DIR.exists():
        print("[CLEAN] Removing previous dist directory...")
        shutil.rmtree(DIST_DIR, ignore_errors=True)

    # 2. Run PyInstaller
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", str(SPEC_FILE)]
    print(f"[BUILD] Executing: {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=BASE_DIR)

    if res.returncode != 0:
        print("[ERROR] PyInstaller build failed!")
        sys.exit(1)

    app_out_dir = DIST_DIR / "AIAttendanceSystem"
    exe_path = app_out_dir / "AIAttendanceSystem.exe"

    if not exe_path.exists():
        print(f"[ERROR] Expected executable not found at: {exe_path}")
        sys.exit(1)

    # 3. Create launchers
    create_bat_launcher(app_out_dir)
    create_bat_launcher(BASE_DIR)

    print("\n" + "=" * 60)
    print("[SUCCESS] Standalone Windows package compiled successfully!")
    print(f"[OUTPUT] Portable App Path: {app_out_dir}")
    print(f"[OUTPUT] Executable Path  : {exe_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
