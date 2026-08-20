"""
Dedicated CustomTkinter Visual Analytics View Component for AI-Enabled Smart Attendance System.
Provides interactive 4-card grid rendering for Daily Trends, Status Proportions, Monthly Trends,
and Student Performance Categories using lightweight CPU-first Matplotlib canvas rendering.
"""

import logging
from datetime import date

try:
    import customtkinter as ctk
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

from app.analytics import (
    get_daily_attendance_trend,
    get_status_distribution,
    get_monthly_attendance_trend,
    get_student_performance_distribution,
)
from app.analytics.chart_renderer import (
    create_daily_trend_figure,
    create_status_distribution_figure,
    create_monthly_trend_figure,
    create_student_performance_figure,
    embed_figure_in_tkinter,
    cleanup_figure_canvas,
    HAS_MATPLOTLIB,
)

logger = logging.getLogger(__name__)


class AnalyticsViewFrame(ctk.CTkFrame):
    """
    Main Visual Analytics UI View component.
    """

    def __init__(self, parent):
        if not HAS_GUI:
            raise RuntimeError("CustomTkinter UI framework is not available.")

        super().__init__(parent)

        self._canvases = [None, None, None, None]
        self._figures = [None, None, None, None]

        self._build_ui()
        self.refresh_charts()

    def _build_ui(self):
        # Header Control Bar
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            header_frame,
            text="Visual Analytics & Attendance Insights",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left", padx=15, pady=10)

        # Control Panel Right
        ctrl_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        ctrl_box.pack(side="right", padx=15, pady=10)

        ctk.CTkLabel(ctrl_box, text="Timeframe:").pack(side="left", padx=(0, 5))
        self.days_var = ctk.StringVar(value="7 Days")
        self.days_menu = ctk.CTkOptionMenu(
            ctrl_box,
            width=100,
            values=["7 Days", "14 Days", "30 Days"],
            variable=self.days_var,
            command=lambda _: self.refresh_charts(),
        )
        self.days_menu.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(ctrl_box, text="Date:").pack(side="left", padx=(0, 5))
        self.date_entry = ctk.CTkEntry(ctrl_box, width=95, placeholder_text="YYYY-MM-DD")
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.pack(side="left", padx=(0, 10))

        self.refresh_btn = ctk.CTkButton(
            ctrl_box,
            text="Refresh Charts",
            width=110,
            command=self.refresh_charts,
        )
        self.refresh_btn.pack(side="left")

        # 4 Chart Grid Panels
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.grid_frame.columnconfigure(0, weight=1)
        self.grid_frame.columnconfigure(1, weight=1)
        self.grid_frame.rowconfigure(0, weight=1)
        self.grid_frame.rowconfigure(1, weight=1)

        # 4 Panel Frames
        self.p1 = ctk.CTkFrame(self.grid_frame)
        self.p1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.p2 = ctk.CTkFrame(self.grid_frame)
        self.p2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.p3 = ctk.CTkFrame(self.grid_frame)
        self.p3.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.p4 = ctk.CTkFrame(self.grid_frame)
        self.p4.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

    def refresh_charts(self):
        """Query analytics services and render all 4 chart figures cleanly."""
        if not HAS_MATPLOTLIB:
            logger.warning("Matplotlib is not installed. Unable to render charts.")
            return

        # Clean existing figure/canvas objects to prevent memory leaks
        for i in range(4):
            cleanup_figure_canvas(self._canvases[i], self._figures[i])
            self._canvases[i] = None
            self._figures[i] = None

        try:
            # Parse timeframe days
            days_str = self.days_var.get()
            days_val = 7
            if "14" in days_str:
                days_val = 14
            elif "30" in days_str:
                days_val = 30

            target_date = self.date_entry.get().strip() or date.today().isoformat()

            # 1. Daily Trend
            t_data = get_daily_attendance_trend(days=days_val)
            fig1, _ = create_daily_trend_figure(t_data, figsize=(4.8, 2.7))
            self._figures[0] = fig1
            self._canvases[0] = embed_figure_in_tkinter(self.p1, fig1)

            # 2. Status Distribution
            s_data = get_status_distribution(target_date=target_date)
            fig2, _ = create_status_distribution_figure(s_data, figsize=(4.8, 2.7))
            self._figures[1] = fig2
            self._canvases[1] = embed_figure_in_tkinter(self.p2, fig2)

            # 3. Monthly Trend
            m_data = get_monthly_attendance_trend(months=6)
            fig3, _ = create_monthly_trend_figure(m_data, figsize=(4.8, 2.7))
            self._figures[2] = fig3
            self._canvases[2] = embed_figure_in_tkinter(self.p3, fig3)

            # 4. Student Performance
            p_data = get_student_performance_distribution()
            fig4, _ = create_student_performance_figure(p_data, figsize=(4.8, 2.7))
            self._figures[3] = fig4
            self._canvases[3] = embed_figure_in_tkinter(self.p4, fig4)

        except Exception as e:
            logger.error(f"Failed to refresh analytics charts: {e}")

    def destroy(self):
        """Cleanly destroy canvas widgets and close Matplotlib figures on frame destruction."""
        for i in range(4):
            cleanup_figure_canvas(self._canvases[i], self._figures[i])
            self._canvases[i] = None
            self._figures[i] = None
        super().destroy()
