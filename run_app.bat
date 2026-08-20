@echo off
title AI-Enabled Smart Attendance System
echo Launching AI-Enabled Smart Attendance System...
set "APP_DIR=%~dp0"
if exist "%APP_DIR%AIAttendanceSystem.exe" (
    start "" "%APP_DIR%AIAttendanceSystem.exe"
) else if exist "%APP_DIR%dist\AIAttendanceSystem\AIAttendanceSystem.exe" (
    start "" "%APP_DIR%dist\AIAttendanceSystem\AIAttendanceSystem.exe"
) else (
    echo Error: AIAttendanceSystem.exe not found.
    pause
)
