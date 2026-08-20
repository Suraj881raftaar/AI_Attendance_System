"""
Reusable UI Components Module for AI-Enabled Smart Attendance System.
Provides standard ConfirmationDialog, EmptyStateWidget, and UI visual styling helpers.
"""

import logging
from typing import Callable, Optional

try:
    import customtkinter as ctk
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

logger = logging.getLogger(__name__)


class ConfirmationDialog(ctk.CTkToplevel):
    """
    Modal confirmation dialog for destructive or sensitive user actions.
    """

    def __init__(
        self,
        parent,
        title: str = "Confirm Action",
        message: str = "Are you sure you want to proceed?",
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        confirm_color: str = "red",
        on_confirm: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
    ):
        if not HAS_GUI:
            raise RuntimeError("CustomTkinter UI framework is not available.")

        super().__init__(parent)

        self.title(title)
        self.geometry("380x200")
        self.resizable(False, False)

        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.grab_set()

        # Center dialog relative to parent
        try:
            if parent is not None:
                self.update_idletasks()
                px = parent.winfo_rootx()
                py = parent.winfo_rooty()
                pw = parent.winfo_width()
                ph = parent.winfo_height()
                x = px + (pw - 380) // 2
                y = py + (ph - 200) // 2
                self.geometry(f"+{x}+{y}")
        except Exception as e:
            logger.debug(f"Could not center confirmation dialog: {e}")

        self._build_ui(message, confirm_text, cancel_text, confirm_color)

    def _build_ui(self, message: str, confirm_text: str, cancel_text: str, confirm_color: str):
        ctk.CTkLabel(
            self,
            text=message,
            font=("Roboto", 13),
            wraplength=340,
        ).pack(expand=True, padx=20, pady=(20, 10))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=25, pady=(0, 20))

        ctk.CTkButton(
            btn_frame,
            text=confirm_text,
            fg_color=confirm_color,
            hover_color="darkred" if confirm_color == "red" else "darkgreen",
            command=self._handle_confirm,
        ).pack(side="left", padx=5, expand=True)

        ctk.CTkButton(
            btn_frame,
            text=cancel_text,
            fg_color="gray",
            command=self._handle_cancel,
        ).pack(side="right", padx=5, expand=True)

    def _handle_confirm(self):
        if self.on_confirm:
            try:
                self.on_confirm()
            except Exception as e:
                logger.error(f"Error during confirmation callback: {e}")
        self.destroy()

    def _handle_cancel(self):
        if self.on_cancel:
            try:
                self.on_cancel()
            except Exception as e:
                logger.error(f"Error during cancellation callback: {e}")
        self.destroy()


class EmptyStateWidget(ctk.CTkFrame):
    """
    Reusable placeholder component for empty tables, search results, or record lists.
    """

    def __init__(
        self,
        parent,
        title: str = "No Data Available",
        subtitle: str = "No records match the current criteria.",
    ):
        if not HAS_GUI:
            raise RuntimeError("CustomTkinter UI framework is not available.")

        super().__init__(parent, fg_color="transparent")

        ctk.CTkLabel(
            self,
            text="[ Empty State ]",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="gray",
        ).pack(pady=(15, 2))

        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(pady=(0, 2))

        ctk.CTkLabel(
            self,
            text=subtitle,
            font=ctk.CTkFont(size=11),
            text_color="gray",
        ).pack(pady=(0, 15))
