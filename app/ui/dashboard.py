"""
Dedicated CustomTkinter Management Dashboard UI View Component for AI-Enabled Smart Attendance System.
Provides summary statistics cards (Total Students, Present Today, Absent Today, Attendance %),
recent attendance activity table, quick action navigation buttons, and auto-refresh timer controls.
"""

import logging
from datetime import datetime
from typing import Callable, Optional, Dict, Any, List

try:
    import customtkinter as ctk
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

from app.dashboard import get_dashboard_metrics
from app.ai.config import get_ai_runtime_status

logger = logging.getLogger(__name__)


class DashboardViewFrame(ctk.CTkFrame):
    """
    Main Management Dashboard UI View frame.
    """

    def __init__(
        self,
        parent,
        on_navigate_attendance: Optional[Callable] = None,
        on_navigate_students: Optional[Callable] = None,
    ):
        if not HAS_GUI:
            raise RuntimeError("CustomTkinter UI framework is not available.")

        super().__init__(parent)

        self.on_navigate_attendance = on_navigate_attendance
        self.on_navigate_students = on_navigate_students

        self._auto_refresh_timer: Optional[str] = None
        self._refresh_interval_ms: int = 10000  # 10 second refresh interval

        self._build_ui()
        self.refresh_dashboard()
        self._schedule_auto_refresh()

    def _build_ui(self):
        # Top Header Banner
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=15, pady=10)

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(
            title_box,
            text="Management Dashboard",
            font=("Roboto", 22, "bold"),
        ).pack(side="left")

        # AI Status Badge
        ai_status = get_ai_runtime_status()
        ai_color = "green" if ai_status["is_available"] else "orange"
        ctk.CTkLabel(
            title_box,
            text=f"AI Engine: {ai_status['status']}",
            font=("Roboto", 12, "bold"),
            text_color=ai_color,
        ).pack(side="right")

        # Summary Statistics Cards (4 Cards Grid)
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=15, pady=5)

        self.card_total = self._create_card(stats_frame, "TOTAL STUDENTS", "0", "gray")
        self.card_total.pack(side="left", expand=True, fill="both", padx=5)

        self.card_present = self._create_card(stats_frame, "PRESENT TODAY", "0", "green")
        self.card_present.pack(side="left", expand=True, fill="both", padx=5)

        self.card_absent = self._create_card(stats_frame, "ABSENT TODAY", "0", "orange")
        self.card_absent.pack(side="left", expand=True, fill="both", padx=5)

        self.card_pct = self._create_card(stats_frame, "ATTENDANCE %", "0.0%", "blue")
        self.card_pct.pack(side="left", expand=True, fill="both", padx=5)

        # Middle Content: Left (Recent Activity Table), Right (Quick Actions)
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Left Column: Recent Activity Table
        left_col = ctk.CTkFrame(content_frame)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 5))

        act_header = ctk.CTkFrame(left_col, fg_color="transparent")
        act_header.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(
            act_header,
            text="Recent Attendance Activity",
            font=("Roboto", 16, "bold"),
        ).pack(side="left")

        self.last_updated_label = ctk.CTkLabel(
            act_header,
            text="Last Updated: Just now",
            font=("Roboto", 11),
            text_color="gray",
        )
        self.last_updated_label.pack(side="right")

        # Table Scrollable Frame
        self.table_scroll = ctk.CTkScrollableFrame(left_col)
        self.table_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Table Header Row
        self._build_table_header()

        # Right Column: Quick Action Buttons & Status Panel
        right_col = ctk.CTkFrame(content_frame, width=280)
        right_col.pack(side="right", fill="both", padx=(5, 0))

        actions_box = ctk.CTkFrame(right_col)
        actions_box.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            actions_box,
            text="Quick Actions",
            font=("Roboto", 14, "bold"),
        ).pack(anchor="w", padx=10, pady=(8, 6))

        self.cam_action_btn = ctk.CTkButton(
            actions_box,
            text="Start Attendance Camera",
            font=("Roboto", 13, "bold"),
            fg_color="green",
            hover_color="darkgreen",
            command=self._handle_navigate_attendance,
        )
        self.cam_action_btn.pack(fill="x", padx=10, pady=5)

        self.stu_action_btn = ctk.CTkButton(
            actions_box,
            text="Add New Student",
            font=("Roboto", 13, "bold"),
            command=self._handle_navigate_students,
        )
        self.stu_action_btn.pack(fill="x", padx=10, pady=5)

        self.refresh_btn = ctk.CTkButton(
            actions_box,
            text="Refresh Dashboard",
            fg_color="gray",
            command=self.refresh_dashboard,
        )
        self.refresh_btn.pack(fill="x", padx=10, pady=(5, 10))

    def _create_card(self, parent, title: str, initial_val: str, color_theme: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(parent)
        ctk.CTkLabel(
            card,
            text=title,
            font=("Roboto", 11, "bold"),
            text_color="gray",
        ).pack(pady=(8, 0))
        val_lbl = ctk.CTkLabel(
            card,
            text=initial_val,
            font=("Roboto", 22, "bold"),
        )
        val_lbl.pack(pady=(0, 8))
        card.value_label = val_lbl  # type: ignore
        return card

    def _build_table_header(self):
        header_row = ctk.CTkFrame(self.table_scroll, fg_color="gray30")
        header_row.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(header_row, text="Student Name", width=140, anchor="w", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=5, pady=4)
        ctk.CTkLabel(header_row, text="Student ID", width=100, anchor="w", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=5, pady=4)
        ctk.CTkLabel(header_row, text="Class", width=70, anchor="w", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=5, pady=4)
        ctk.CTkLabel(header_row, text="Time", width=70, anchor="w", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=5, pady=4)
        ctk.CTkLabel(header_row, text="Status", width=70, anchor="w", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=5, pady=4)

    def refresh_dashboard(self):
        """Query database and update stat cards and activity table."""
        try:
            metrics = get_dashboard_metrics()

            # Update Stat Cards
            self.card_total.value_label.configure(text=str(metrics["total_students"]))  # type: ignore
            self.card_present.value_label.configure(text=str(metrics["present_today"]))  # type: ignore
            self.card_absent.value_label.configure(text=str(metrics["absent_today"]))  # type: ignore
            self.card_pct.value_label.configure(text=f"{metrics['attendance_percentage']}%")  # type: ignore

            # Update Timestamp Label
            now_str = datetime.now().strftime("%H:%M:%S")
            self.last_updated_label.configure(text=f"Last Updated: {now_str}")

            # Populate Activity Table
            self._update_activity_table(metrics.get("recent_activity", []))

        except Exception as e:
            logger.error(f"Failed to refresh dashboard: {e}")

    def _update_activity_table(self, recent_list: List[Dict[str, Any]]):
        # Clear existing table rows (preserve header row 0)
        for child in self.table_scroll.winfo_children()[1:]:
            child.destroy()

        if not recent_list:
            empty_frame = ctk.CTkFrame(self.table_scroll, fg_color="transparent")
            empty_frame.pack(fill="x", pady=15)
            ctk.CTkLabel(
                empty_frame,
                text="No attendance recorded yet for today.",
                text_color="gray",
            ).pack()
            return

        for item in recent_list:
            row_frame = ctk.CTkFrame(self.table_scroll)
            row_frame.pack(fill="x", pady=2)

            ctk.CTkLabel(row_frame, text=item.get("student_name", "-"), width=140, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row_frame, text=item.get("student_code", "-"), width=100, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row_frame, text=item.get("class_section", "-"), width=70, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row_frame, text=item.get("attendance_time", "-"), width=70, anchor="w").pack(side="left", padx=5)

            status_val = item.get("status", "Present")
            status_color = "green" if status_val == "Present" else "orange"
            ctk.CTkLabel(row_frame, text=status_val, width=70, text_color=status_color, anchor="w").pack(side="left", padx=5)

    def _handle_navigate_attendance(self):
        if self.on_navigate_attendance:
            self.on_navigate_attendance()

    def _handle_navigate_students(self):
        if self.on_navigate_students:
            self.on_navigate_students()

    def _schedule_auto_refresh(self):
        self.refresh_dashboard()
        self._auto_refresh_timer = self.after(self._refresh_interval_ms, self._schedule_auto_refresh)

    def destroy(self):
        """Cancel auto-refresh timer callback upon frame destruction to prevent orphaned timers."""
        if self._auto_refresh_timer is not None:
            try:
                self.after_cancel(self._auto_refresh_timer)
            except Exception as e:
                logger.debug(f"Error cancelling dashboard refresh timer: {e}")
            self._auto_refresh_timer = None
        super().destroy()
