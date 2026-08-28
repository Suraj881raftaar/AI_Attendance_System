"""
Login UI component for AI-Enabled Smart Attendance System.
Built using CustomTkinter for desktop authentication user interface.
"""

import logging
from typing import Callable, Optional

try:
    import customtkinter as ctk
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

from app.auth import login, is_first_run, setup_first_admin

logger = logging.getLogger(__name__)


class LoginFrame:
    """CustomTkinter Login Frame for user authentication."""

    def __init__(self, parent_container, on_login_success: Optional[Callable] = None):
        if not HAS_GUI:
            raise RuntimeError("CustomTkinter UI framework is not available.")

        self.parent = parent_container
        self.on_login_success = on_login_success

        self.frame = ctk.CTkFrame(self.parent)
        self.frame.pack(expand=True, fill="both", padx=20, pady=20)

        self._build_ui()

    def _build_ui(self):
        # Header Label
        self.title_label = ctk.CTkLabel(
            self.frame,
            text="AI Attendance System",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.title_label.pack(pady=(40, 10))

        self.subtitle_label = ctk.CTkLabel(
            self.frame,
            text="Please sign in to continue",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        self.subtitle_label.pack(pady=(0, 20))

        # Username Input
        self.username_entry = ctk.CTkEntry(
            self.frame,
            placeholder_text="Username",
            width=300,
            height=40,
        )
        self.username_entry.pack(pady=10)

        # Password Input
        self.password_entry = ctk.CTkEntry(
            self.frame,
            placeholder_text="Password",
            show="*",
            width=300,
            height=40,
        )
        self.password_entry.pack(pady=10)

        # Status / Feedback Label
        self.status_label = ctk.CTkLabel(
            self.frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="red",
        )
        self.status_label.pack(pady=5)

        # First-Run Check & Submit Button
        if is_first_run():
            self.subtitle_label.configure(text="First-Run Setup: Create Admin Account")
            self.submit_btn = ctk.CTkButton(
                self.frame,
                text="Create Admin & Login",
                width=300,
                height=40,
                command=self._handle_first_run_setup,
            )
        else:
            self.submit_btn = ctk.CTkButton(
                self.frame,
                text="Login",
                width=300,
                height=40,
                command=self._handle_login,
            )

        self.submit_btn.pack(pady=(15, 30))

    def _handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.frame.winfo_exists():
            self.status_label.configure(text="", text_color="red")

        try:
            user = login(username, password)
            if self.frame.winfo_exists():
                self.status_label.configure(text="Login successful!", text_color="green")
            if self.on_login_success:
                self.on_login_success(user)
        except ValueError as e:
            if self.frame.winfo_exists():
                self.status_label.configure(text=str(e), text_color="red")
        except Exception as e:
            logger.error(f"Unexpected login error: {e}")
            if self.frame.winfo_exists():
                self.status_label.configure(text="An unexpected error occurred. Please try again.", text_color="red")

    def _handle_first_run_setup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.frame.winfo_exists():
            self.status_label.configure(text="", text_color="red")

        try:
            setup_first_admin(username, password)
            user = login(username, password)
            if self.frame.winfo_exists():
                self.status_label.configure(text="Admin created & logged in!", text_color="green")
            if self.on_login_success:
                self.on_login_success(user)
        except ValueError as e:
            if self.frame.winfo_exists():
                self.status_label.configure(text=str(e), text_color="red")
        except Exception as e:
            logger.error(f"Unexpected setup error: {e}")
            if self.frame.winfo_exists():
                self.status_label.configure(text="An unexpected error occurred.", text_color="red")


class LoginWindow(ctk.CTk):
    """Top-level CustomTkinter Window for User Login."""

    def __init__(self, on_login_success: Optional[Callable] = None):
        if not HAS_GUI:
            raise RuntimeError("CustomTkinter UI framework is not available.")

        super().__init__()
        self.title("AI Attendance System — Authentication")
        self.geometry("500x420")
        self.resizable(False, False)

        self.on_login_success = on_login_success

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.login_frame = LoginFrame(self, on_login_success=self._handle_success)

    def _handle_success(self, user_info=None):
        cb = self.on_login_success
        if self.winfo_exists():
            self.destroy()
        if cb:
            cb(user_info)

