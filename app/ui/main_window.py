"""
Main Application Shell Container Window for AI-Enabled Smart Attendance System.
Provides a unified navigation sidebar, header status bar (user info, role badge, AI engine status),
and smooth view switching between Dashboard, Students, Attendance, Reports, and Analytics.
"""

import logging
from typing import Optional, Callable

try:
    import customtkinter as ctk
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

from app.auth import get_session
from app.ai.config import get_ai_runtime_status
from app.ui.components import ConfirmationDialog
from app.ui.dashboard import DashboardViewFrame
from app.ui.students import StudentManagementFrame
from app.ui.attendance import AttendanceViewFrame
from app.ui.reports import ReportsViewFrame
from app.ui.analytics import AnalyticsViewFrame

logger = logging.getLogger(__name__)


class MainWindow(ctk.CTk):
    """
    Primary desktop application shell hosting all navigation tabs and active view frames.
    """

    def __init__(self, on_logout: Optional[Callable] = None):
        if not HAS_GUI:
            raise RuntimeError("CustomTkinter UI framework is not available.")

        super().__init__()

        self.title("AI-Enabled Smart Attendance System")
        self.geometry("1100x700")
        self.minsize(950, 600)

        self.on_logout_callback = on_logout
        self.active_view = None
        self.current_tab = "Dashboard"

        # Apply dark-blue theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self._build_ui()
        self.show_view("Dashboard")

    def _build_ui(self):
        # --------------------------------------------------------------------
        # TOPBAR / HEADER STATUS BAR
        # --------------------------------------------------------------------
        self.topbar = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.topbar.pack(side="top", fill="x")

        # Left Title
        title_lbl = ctk.CTkLabel(
            self.topbar,
            text="AI-Enabled Smart Attendance System",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title_lbl.pack(side="left", padx=15, pady=10)

        # Right Actions Panel
        top_right = ctk.CTkFrame(self.topbar, fg_color="transparent")
        top_right.pack(side="right", padx=15, pady=5)

        # User session metadata
        session = get_session()
        user_info = session.get_current_user() if session.is_logged_in() else {}
        username = user_info.get("username", "Guest")
        role = user_info.get("role", "teacher").upper()

        # Role Badge Color
        role_color = "#3498DB" if role == "ADMIN" else "#2ECC71"
        ctk.CTkLabel(
            top_right,
            text=f"User: {username}",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            top_right,
            text=f"[{role}]",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=role_color,
        ).pack(side="left", padx=(0, 15))

        # AI Runtime Status Indicator
        ai_status = get_ai_runtime_status()
        ai_color = "green" if ai_status["is_available"] else "orange"
        ctk.CTkLabel(
            top_right,
            text=f"AI Status: {ai_status['status']}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=ai_color,
        ).pack(side="left", padx=(0, 15))

        # Logout Button
        logout_btn = ctk.CTkButton(
            top_right,
            text="Logout",
            width=70,
            fg_color="red",
            hover_color="darkred",
            command=self._confirm_logout,
        )
        logout_btn.pack(side="left")

        # --------------------------------------------------------------------
        # BODY CONTAINER (SIDEBAR LEFT + CONTENT AREA RIGHT)
        # --------------------------------------------------------------------
        self.body_container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.body_container.pack(fill="both", expand=True)

        # SIDEBAR NAVIGATION MENU (LEFT)
        self.sidebar = ctk.CTkFrame(self.body_container, width=180, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(
            self.sidebar,
            text="NAVIGATION",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray",
        ).pack(anchor="w", padx=15, pady=(15, 10))

        self.nav_buttons = {}

        tabs = [
            ("Dashboard", self._nav_dashboard),
            ("Students", self._nav_students),
            ("AI Attendance", self._nav_attendance),
            ("Reports", self._nav_reports),
            ("Analytics", self._nav_analytics),
        ]

        for name, cmd in tabs:
            btn = ctk.CTkButton(
                self.sidebar,
                text=name,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                command=cmd,
            )
            btn.pack(fill="x", padx=10, pady=4)
            self.nav_buttons[name] = btn

        # CONTENT AREA FRAME (RIGHT)
        self.content_area = ctk.CTkFrame(self.body_container, fg_color="transparent")
        self.content_area.pack(side="right", fill="both", expand=True)

    def show_view(self, view_name: str):
        """Switch active view frame cleanly."""
        self.current_tab = view_name

        # Update sidebar button highlight styles
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(fg_color="#1F497D", text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"))

        # Destroy old view frame safely
        if self.active_view is not None:
            try:
                self.active_view.destroy()
            except Exception as e:
                logger.debug(f"Error destroying previous view frame: {e}")
            self.active_view = None

        # Instantiate requested view frame
        if view_name == "Dashboard":
            self.active_view = DashboardViewFrame(
                self.content_area,
                on_navigate_attendance=lambda: self.show_view("AI Attendance"),
                on_navigate_students=lambda: self.show_view("Students"),
            )
        elif view_name == "Students":
            self.active_view = StudentManagementFrame(self.content_area)
        elif view_name == "AI Attendance":
            self.active_view = AttendanceViewFrame(self.content_area)
        elif view_name == "Reports":
            self.active_view = ReportsViewFrame(self.content_area)
        elif view_name == "Analytics":
            self.active_view = AnalyticsViewFrame(self.content_area)

        if self.active_view is not None:
            self.active_view.pack(fill="both", expand=True)

    def _nav_dashboard(self):
        self.show_view("Dashboard")

    def _nav_students(self):
        self.show_view("Students")

    def _nav_attendance(self):
        self.show_view("AI Attendance")

    def _nav_reports(self):
        self.show_view("Reports")

    def _nav_analytics(self):
        self.show_view("Analytics")

    def _confirm_logout(self):
        """Ask for confirmation before logging out."""
        ConfirmationDialog(
            parent=self,
            title="Confirm Logout",
            message="Are you sure you want to log out of the AI Attendance System?",
            confirm_text="Log Out",
            confirm_color="red",
            on_confirm=self._do_logout,
        )

    def _do_logout(self):
        """Destroy session, destroy MainWindow, and trigger logout callback."""
        session = get_session()
        session.clear_session()

        if self.on_logout_callback:
            self.on_logout_callback()
        self.destroy()
