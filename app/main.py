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
from app.database import initialize_database
from app.auth import is_first_run


def print_banner():
    """Display startup banner."""
    print("=" * 60)
    print(f"  {APP_NAME}")
    print(f"  Version: {APP_VERSION}")
    print(f"  Project Type: Class 12 Academic Project")
    print("=" * 60)


def verify_environment():
    """Verify application folders, initialize database, and check python runtime environment."""
    ensure_directories()
    initialize_database()
    print("[INIT] Base Directory :", BASE_DIR)
    print("[INIT] Database Path  :", DATABASE_PATH)
    print("[INIT] Face Data Path :", FACE_DATA_DIR)
    print("[INIT] Models Path    :", MODELS_DIR)
    print("[INIT] Python Version :", sys.version.split()[0])
    print("[INIT] Database initialized successfully.")

    if is_first_run():
        print("[AUTH] Status         : First-Run Mode (No Administrator Exists)")
    else:
        print("[AUTH] Status         : User Accounts Configured")

    from app.ai.config import get_ai_runtime_status
    ai_status = get_ai_runtime_status()
    print(f"[AI] Model Status     : {ai_status['status']} ({ai_status['message']})")


def launch_app():
    """Launch the GUI application (Login -> MainWindow)."""
    from app.ui.login import LoginWindow
    from app.ui.main_window import MainWindow

    def start_main_window():
        main_win = MainWindow(on_logout=launch_app)
        main_win.mainloop()

    login = LoginWindow(on_login_success=start_main_window)
    login.mainloop()


def main():
    """Main application launcher."""
    print_banner()
    verify_environment()
    print("\n[READY] STAGE 11 Testing & System Hardening Operational.")

    if (len(sys.argv) > 1 and sys.argv[1] == "--cli-only") or os.environ.get("PYTEST_CURRENT_TEST"):
        return 0

    launch_app()
    return 0


if __name__ == "__main__":
    sys.exit(main())
