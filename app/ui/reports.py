"""
Dedicated CustomTkinter Attendance Reports & Management UI View Component for AI-Enabled Smart Attendance System.
Provides multi-criteria search filtering, interactive attendance table with inline manual correction dialog,
student attendance percentage analytics, and CSV/Excel export buttons.
"""

import logging
from datetime import date
from typing import Optional, List, Dict, Any, Callable

try:
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

from app.reports import (
    search_attendance_records,
    get_student_attendance_summary,
    correct_attendance_record,
    export_attendance_csv,
    export_attendance_excel,
)

logger = logging.getLogger(__name__)


class CorrectionDialog(ctk.CTkToplevel):
    """
    Modal dialog for authorized manual correction of an attendance record's status and time.
    """

    def __init__(self, parent, record: Dict[str, Any], on_saved: Optional[Callable] = None):
        if not HAS_GUI:
            raise RuntimeError("CustomTkinter UI framework is not available.")

        super().__init__(parent)
        self.title("Manual Attendance Correction")
        self.geometry("400x320")
        self.resizable(False, False)

        self.record = record
        self.on_saved = on_saved
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(
            self,
            text="Attendance Record Correction",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(15, 5))

        name = self.record.get("student_name", "Unknown")
        code = self.record.get("student_code", "-")
        rec_date = self.record.get("attendance_date", "-")

        ctk.CTkLabel(
            self,
            text=f"Student: {name} ({code})\nDate: {rec_date}",
            font=ctk.CTkFont(size=12),
        ).pack(pady=5)

        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="x", padx=25, pady=10)

        # Status OptionMenu
        ctk.CTkLabel(form_frame, text="Attendance Status:").pack(anchor="w", padx=10, pady=(8, 2))
        self.status_var = ctk.StringVar(value=self.record.get("status", "Present"))
        self.status_menu = ctk.CTkOptionMenu(
            form_frame,
            values=["Present", "Absent", "Late", "Excused"],
            variable=self.status_var,
        )
        self.status_menu.pack(fill="x", padx=10, pady=(0, 8))

        # Time Entry
        ctk.CTkLabel(form_frame, text="Attendance Time (HH:MM:SS):").pack(anchor="w", padx=10, pady=(4, 2))
        self.time_entry = ctk.CTkEntry(form_frame)
        self.time_entry.insert(0, self.record.get("attendance_time", "09:00:00"))
        self.time_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Error label
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack(pady=2)

        # Action Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=25, pady=10)

        ctk.CTkButton(
            btn_frame,
            text="Save Correction",
            fg_color="green",
            hover_color="darkgreen",
            command=self._handle_save,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color="gray",
            command=self.destroy,
        ).pack(side="right", padx=5)

    def _handle_save(self):
        new_status = self.status_var.get()
        new_time = self.time_entry.get().strip()

        try:
            correct_attendance_record(
                attendance_id=self.record["attendance_id"],
                status=new_status,
                attendance_time=new_time,
            )
            if self.on_saved:
                self.on_saved()
            self.destroy()
        except Exception as e:
            self.error_label.configure(text=f"Correction Error: {e}")


class ReportsViewFrame(ctk.CTkFrame):
    """
    Main Attendance Reports & Management UI View component.
    """

    def __init__(self, parent):
        if not HAS_GUI:
            raise RuntimeError("CustomTkinter UI framework is not available.")

        super().__init__(parent)

        self.current_records: List[Dict[str, Any]] = []
        self.current_summary: List[Dict[str, Any]] = []

        self._build_ui()
        self._handle_search()

    def _build_ui(self):
        # Header Banner
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            header_frame,
            text="Attendance Reports & Records Management",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        # Filter Bar Frame
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(fill="x", padx=15, pady=5)

        # Row 1: Filter Entries
        r1 = ctk.CTkFrame(filter_frame, fg_color="transparent")
        r1.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(r1, text="Start Date:").pack(side="left", padx=(5, 2))
        self.start_date_entry = ctk.CTkEntry(r1, width=95, placeholder_text="YYYY-MM-DD")
        self.start_date_entry.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(r1, text="End Date:").pack(side="left", padx=(5, 2))
        self.end_date_entry = ctk.CTkEntry(r1, width=95, placeholder_text="YYYY-MM-DD")
        self.end_date_entry.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(r1, text="Student Search:").pack(side="left", padx=(5, 2))
        self.student_search_entry = ctk.CTkEntry(r1, width=130, placeholder_text="Name or ID")
        self.student_search_entry.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(r1, text="Status:").pack(side="left", padx=(5, 2))
        self.status_var = ctk.StringVar(value="All")
        self.status_menu = ctk.CTkOptionMenu(
            r1,
            width=95,
            values=["All", "Present", "Absent", "Late", "Excused"],
            variable=self.status_var,
        )
        self.status_menu.pack(side="left", padx=(0, 10))

        # Row 2: Action Buttons (Apply, Reset, Export CSV, Export Excel)
        r2 = ctk.CTkFrame(filter_frame, fg_color="transparent")
        r2.pack(fill="x", padx=10, pady=(0, 8))

        ctk.CTkButton(
            r2,
            text="Apply Filters",
            width=110,
            command=self._handle_search,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            r2,
            text="Reset Filters",
            width=100,
            fg_color="gray",
            command=self._handle_reset,
        ).pack(side="left", padx=5)

        # Export Buttons
        ctk.CTkButton(
            r2,
            text="Export Excel (.xlsx)",
            width=135,
            fg_color="green",
            hover_color="darkgreen",
            command=self._handle_export_excel,
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            r2,
            text="Export CSV (.csv)",
            width=125,
            fg_color="darkblue",
            command=self._handle_export_csv,
        ).pack(side="right", padx=5)

        # Status Message Label
        self.msg_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.msg_label.pack(pady=2)

        # Middle Content: Left (Filtered Attendance Table), Right (Summary Stats Panel)
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Left Column: Filtered Records Table
        left_col = ctk.CTkFrame(content_frame)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(
            left_col,
            text="Filtered Attendance Records",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(8, 4))

        self.table_scroll = ctk.CTkScrollableFrame(left_col)
        self.table_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Right Column: Student Summary Analytics
        right_col = ctk.CTkFrame(content_frame, width=280)
        right_col.pack(side="right", fill="both", padx=(5, 0))

        ctk.CTkLabel(
            right_col,
            text="Student Analytics Summary",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(8, 4))

        self.summary_scroll = ctk.CTkScrollableFrame(right_col)
        self.summary_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _handle_search(self):
        s_date = self.start_date_entry.get().strip() or None
        e_date = self.end_date_entry.get().strip() or None
        s_query = self.student_search_entry.get().strip() or None
        st_filter = self.status_var.get()

        try:
            self.current_records = search_attendance_records(
                start_date=s_date,
                end_date=e_date,
                student_query=s_query,
                status_filter=st_filter,
            )

            self.current_summary = get_student_attendance_summary(
                start_date=s_date,
                end_date=e_date,
            )

            self._populate_records_table()
            self._populate_summary_panel()

            self.msg_label.configure(
                text=f"Found {len(self.current_records)} matching attendance records.",
                text_color="gray",
            )
        except Exception as e:
            self.msg_label.configure(text=f"Search Error: {e}", text_color="red")

    def _handle_reset(self):
        self.start_date_entry.delete(0, "end")
        self.end_date_entry.delete(0, "end")
        self.student_search_entry.delete(0, "end")
        self.status_var.set("All")
        self._handle_search()

    def _populate_records_table(self):
        for child in self.table_scroll.winfo_children():
            child.destroy()

        # Header Row
        header_row = ctk.CTkFrame(self.table_scroll, fg_color="gray30")
        header_row.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(header_row, text="Name", width=130, anchor="w", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=4, pady=4)
        ctk.CTkLabel(header_row, text="ID", width=90, anchor="w", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=4, pady=4)
        ctk.CTkLabel(header_row, text="Class", width=60, anchor="w", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=4, pady=4)
        ctk.CTkLabel(header_row, text="Date", width=85, anchor="w", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=4, pady=4)
        ctk.CTkLabel(header_row, text="Time", width=65, anchor="w", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=4, pady=4)
        ctk.CTkLabel(header_row, text="Status", width=65, anchor="w", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=4, pady=4)
        ctk.CTkLabel(header_row, text="Action", width=50, anchor="w", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=4, pady=4)

        if not self.current_records:
            empty_frame = ctk.CTkFrame(self.table_scroll, fg_color="transparent")
            empty_frame.pack(fill="x", pady=15)
            ctk.CTkLabel(empty_frame, text="No records match current filter criteria.", text_color="gray").pack()
            return

        for rec in self.current_records:
            row = ctk.CTkFrame(self.table_scroll)
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=rec.get("student_name", "-"), width=130, anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(row, text=rec.get("student_code", "-"), width=90, anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(row, text=rec.get("class_section", "-"), width=60, anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(row, text=rec.get("attendance_date", "-"), width=85, anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(row, text=rec.get("attendance_time", "-"), width=65, anchor="w").pack(side="left", padx=4)

            status_val = rec.get("status", "Present")
            status_color = "green" if status_val == "Present" else "orange"
            ctk.CTkLabel(row, text=status_val, width=65, text_color=status_color, anchor="w").pack(side="left", padx=4)

            rec_ref = rec
            ctk.CTkButton(
                row,
                text="Edit",
                width=45,
                height=22,
                command=lambda r=rec_ref: CorrectionDialog(self.winfo_toplevel(), r, on_saved=self._handle_search),
            ).pack(side="left", padx=4)

    def _populate_summary_panel(self):
        for child in self.summary_scroll.winfo_children():
            child.destroy()

        if not self.current_summary:
            ctk.CTkLabel(self.summary_scroll, text="No student summary data.", text_color="gray").pack(pady=10)
            return

        for item in self.current_summary:
            card = ctk.CTkFrame(self.summary_scroll)
            card.pack(fill="x", pady=4, padx=2)

            ctk.CTkLabel(card, text=f"{item['student_name']} ({item['student_code']})", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=8, pady=(4, 2))
            ctk.CTkLabel(
                card,
                text=f"Days: {item['total_days']} | Pres: {item['present_count']} | Abs: {item['absent_count']} | {item['attendance_percentage']}%",
                font=ctk.CTkFont(size=11),
                text_color="gray",
            ).pack(anchor="w", padx=8, pady=(0, 4))

    def _handle_export_csv(self):
        if not self.current_records:
            self.msg_label.configure(text="Export Warning: No records to export.", text_color="orange")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Attendance Records to CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"attendance_report_{date.today().isoformat()}.csv",
        )
        if not file_path:
            return

        try:
            out_path = export_attendance_csv(self.current_records, file_path)
            self.msg_label.configure(text=f"CSV exported successfully to {out_path.name}", text_color="green")
        except Exception as e:
            self.msg_label.configure(text=f"CSV Export Error: {e}", text_color="red")

    def _handle_export_excel(self):
        if not self.current_records:
            self.msg_label.configure(text="Export Warning: No records to export.", text_color="orange")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Attendance Workbook to Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile=f"attendance_report_{date.today().isoformat()}.xlsx",
        )
        if not file_path:
            return

        try:
            out_path = export_attendance_excel(
                records=self.current_records,
                output_path=file_path,
                summary_data=self.current_summary,
            )
            self.msg_label.configure(text=f"Excel workbook exported successfully to {out_path.name}", text_color="green")
        except Exception as e:
            self.msg_label.configure(text=f"Excel Export Error: {e}", text_color="red")
