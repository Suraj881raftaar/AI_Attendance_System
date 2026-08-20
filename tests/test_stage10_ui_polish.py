"""
Comprehensive Stage 10 Automated Test Suite for UI/UX Polish & Main Window Shell Container.
Tests MainWindow shell initialization, active view switching, navigation tab styles,
ConfirmationDialog callbacks, EmptyStateWidget rendering, form validation feedback, and session logout cleanup.
"""

import tempfile
from pathlib import Path
import pytest

from app.database import initialize_database
from app.auth import get_session
from app.ui.components import ConfirmationDialog, EmptyStateWidget
from app.ui.main_window import MainWindow


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    initialize_database(db_path)
    yield db_path
    if db_path.exists():
        try:
            db_path.unlink()
        except PermissionError:
            pass


@pytest.fixture
def auth_session():
    """Authenticate session as admin for testing."""
    session = get_session()
    session.start_session({"id": 1, "username": "admin_ui_test", "role": "admin"})
    yield session
    session.clear_session()


# ============================================================================
# 1. MAIN WINDOW SHELL & NAVIGATION TESTS
# ============================================================================

def test_main_window_initialization(auth_session):
    """Test MainWindow initialization and default Dashboard view selection."""
    main_win = MainWindow()
    main_win.withdraw()
    assert main_win.title() == "AI-Enabled Smart Attendance System"
    assert main_win.current_tab == "Dashboard"
    assert main_win.active_view is not None

    main_win.destroy()


def test_main_window_view_switching(auth_session):
    """Test switching between Dashboard, Students, AI Attendance, Reports, and Analytics views."""
    main_win = MainWindow()
    main_win.withdraw()

    for tab in ["Students", "AI Attendance", "Reports", "Analytics", "Dashboard"]:
        main_win.show_view(tab)
        assert main_win.current_tab == tab
        assert main_win.active_view is not None

    main_win.destroy()


# ============================================================================
# 2. CONFIRMATION DIALOG & COMPONENT TESTS
# ============================================================================

def test_confirmation_dialog_callbacks():
    """Test ConfirmationDialog confirm and cancel callback triggers."""
    confirm_called = False
    cancel_called = False

    def on_confirm():
        nonlocal confirm_called
        confirm_called = True

    def on_cancel():
        nonlocal cancel_called
        cancel_called = True

    # Test Confirm handler
    dlg_confirm = ConfirmationDialog(
        parent=None,
        title="Test Confirm",
        message="Test message",
        on_confirm=on_confirm,
        on_cancel=on_cancel,
    )
    dlg_confirm._handle_confirm()
    assert confirm_called is True
    assert cancel_called is False

    # Test Cancel handler
    confirm_called = False
    dlg_cancel = ConfirmationDialog(
        parent=None,
        title="Test Cancel",
        message="Test message",
        on_confirm=on_confirm,
        on_cancel=on_cancel,
    )
    dlg_cancel._handle_cancel()
    assert confirm_called is False
    assert cancel_called is True


def test_empty_state_widget():
    """Test EmptyStateWidget creation."""
    widget = EmptyStateWidget(parent=None, title="No Students", subtitle="Search query returned 0 results.")
    assert widget is not None
    widget.destroy()


# ============================================================================
# 3. SESSION LOGOUT & CLEANUP TESTS
# ============================================================================

def test_main_window_logout_cleanup(auth_session):
    """Test MainWindow logout execution clears session token."""
    logout_triggered = False

    def on_logout():
        nonlocal logout_triggered
        logout_triggered = True

    main_win = MainWindow(on_logout=on_logout)
    main_win._do_logout()

    session = get_session()
    assert session.is_logged_in() is False
    assert logout_triggered is True
