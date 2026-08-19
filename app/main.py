"""
Application entry point module for AI-Enabled Smart Attendance System.
"""

import sys
import os
from pathlib import Path

from app.config import (
    APP_NAME,
    APP_VERSION,
    BASE_DIR,
    DATABASE_PATH,
    FACE_DATA_DIR,
    MODELS_DIR,
    ensure_directories,
)


def print_banner():
    """Display startup banner."""
    print("=" * 60)
    print(f"  {APP_NAME}")
    print(f"  Version: {APP_VERSION}")
    print(f"  Project Type: Class 12 Academic Project")
    print("=" * 60)


def verify_environment():
    """Verify application folders and python runtime environment."""
    ensure_directories()
    print("[INIT] Base Directory :", BASE_DIR)
    print("[INIT] Database Path  :", DATABASE_PATH)
    print("[INIT] Face Data Path :", FACE_DATA_DIR)
    print("[INIT] Models Path    :", MODELS_DIR)
    print("[INIT] Python Version :", sys.version.split()[0])
    print("[INIT] Environment setup verified successfully.")


def main():
    """Main application launcher."""
    print_banner()
    verify_environment()
    print("\n[READY] STAGE 0 Project Initialization Complete.")
    print("[INFO] Ready for STAGE 1 (Database & Core Foundation).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
