"""
Student Management UI component for AI-Enabled Smart Attendance System.
Built using CustomTkinter for desktop student administration.
"""

import logging
from typing import Callable, Optional, List, Dict, Any

try:
    import customtkinter as ctk
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

from app.students import (
    add_student,
    update_student_details,
    deactivate_student_record,
    get_student_detail,
    list_all_students,
    find_students,
)

logger = logging.getLogger(__name__)


class StudentManagementFrame:
    """CustomTkinter Student Management View Frame."""

    def __init__(self, parent_container):
        if not HAS_GUI:
            raise RuntimeError("CustomTkinter UI framework is not available.")

        self.parent = parent_container
        self.frame = ctk.CTkFrame(self.parent)
        self.frame.pack(expand=True, fill="both", padx=15, pady=15)

        self.active_filter = True
        self._build_ui()
        self.refresh_student_list()

    def _build_ui(self):
        # Header Controls Bar
        self.top_bar = ctk.CTkFrame(self.frame, height=50)
        self.top_bar.pack(fill="x", padx=10, pady=(10, 5))

        self.title_label = ctk.CTkLabel(
            self.top_bar,
            text="Student Records",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.title_label.pack(side="left", padx=15, pady=10)

        # Search Bar
        self.search_entry = ctk.CTkEntry(
            self.top_bar,
            placeholder_text="Search ID, Name, or Roll...",
            width=250,
        )
        self.search_entry.pack(side="left", padx=5, pady=10)

        self.search_btn = ctk.CTkButton(
            self.top_bar,
            text="Search",
            width=80,
            command=self._handle_search,
        )
        self.search_btn.pack(side="left", padx=5, pady=10)

        self.clear_btn = ctk.CTkButton(
            self.top_bar,
            text="Reset",
            width=70,
            fg_color="gray",
            command=self._handle_reset_search,
        )
        self.clear_btn.pack(side="left", padx=5, pady=10)

        # Add Student Button
        self.add_btn = ctk.CTkButton(
            self.top_bar,
            text="+ Add Student",
            fg_color="green",
            hover_color="darkgreen",
            command=self._open_add_student_dialog,
        )
        self.add_btn.pack(side="right", padx=15, pady=10)

        # Status Label
        self.status_label = ctk.CTkLabel(
            self.frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.status_label.pack(fill="x", padx=15, pady=2)

        # Student Table Scrollable Container
        self.scroll_container = ctk.CTkScrollableFrame(self.frame)
        self.scroll_container.pack(expand=True, fill="both", padx=10, pady=5)

    def refresh_student_list(self, students: Optional[List[Dict[str, Any]]] = None):
        """Re-render the student list table."""
        # Clear existing rows
        for child in self.scroll_container.winfo_children():
            child.destroy()

        if students is None:
            try:
                students = list_all_students(active_only=self.active_filter)
            except Exception as e:
                self.status_label.configure(text=f"Error loading students: {e}", text_color="red")
                return

        if not students:
            no_data_label = ctk.CTkLabel(
                self.scroll_container,
                text="No student records found.",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="gray",
            )
            no_data_label.pack(pady=40)
            self.status_label.configure(text="Total Records: 0", text_color="gray")
            return

        self.status_label.configure(text=f"Total Records Displayed: {len(students)}", text_color="gray")

        # Table Header
        headers_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        headers_frame.pack(fill="x", pady=5)

        cols = [("ID Code", 120), ("Full Name", 180), ("Class", 80), ("Sec", 60), ("Roll", 80), ("Status", 80), ("Actions", 150)]
        for col_name, col_width in cols:
            lbl = ctk.CTkLabel(headers_frame, text=col_name, width=col_width, font=ctk.CTkFont(size=12, weight="bold"), anchor="w")
            lbl.pack(side="left", padx=5)

        # Render Rows
        for student in students:
            row_frame = ctk.CTkFrame(self.scroll_container)
            row_frame.pack(fill="x", pady=3)

            ctk.CTkLabel(row_frame, text=student["student_id"], width=120, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row_frame, text=student["name"], width=180, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row_frame, text=student["class_name"], width=80, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row_frame, text=student["section"], width=60, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row_frame, text=student.get("roll_number") or "-", width=80, anchor="w").pack(side="left", padx=5)
            
            # Status Badge
            status_text = student.get("status", "active").capitalize()
            status_color = "green" if status_text == "Active" else "orange"
            ctk.CTkLabel(row_frame, text=status_text, width=80, text_color=status_color, anchor="w").pack(side="left", padx=5)

            # Action Buttons
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.pack(side="left", padx=5)

            student_id_val = student["id"]
            edit_btn = ctk.CTkButton(
                actions_frame,
                text="Edit",
                width=50,
                height=25,
                command=lambda sid=student_id_val: self._open_edit_student_dialog(sid),
            )
            edit_btn.pack(side="left", padx=2)

            enroll_btn = ctk.CTkButton(
                actions_frame,
                text="Enroll Face",
                width=75,
                height=25,
                fg_color="blue",
                hover_color="darkblue",
                command=lambda sid=student_id_val: self._open_enroll_face_dialog(sid),
            )
            enroll_btn.pack(side="left", padx=2)

            if student.get("status") == "active":
                deact_btn = ctk.CTkButton(
                    actions_frame,
                    text="Deactivate",
                    width=75,
                    height=25,
                    fg_color="red",
                    hover_color="darkred",
                    command=lambda sid=student_id_val: self._handle_deactivate(sid),
                )
                deact_btn.pack(side="left", padx=2)

    def _handle_search(self):
        query = self.search_entry.get().strip()
        try:
            results = find_students(query, active_only=self.active_filter)
            self.refresh_student_list(results)
        except Exception as e:
            self.status_label.configure(text=f"Search failed: {e}", text_color="red")

    def _handle_reset_search(self):
        self.search_entry.delete(0, "end")
        self.refresh_student_list()

    def _handle_deactivate(self, id_val: int):
        try:
            deactivate_student_record(id_val)
            self.refresh_student_list()
        except Exception as e:
            self.status_label.configure(text=f"Deactivation failed: {e}", text_color="red")

    def _open_add_student_dialog(self):
        AddStudentDialog(self.parent, on_saved=self.refresh_student_list)

    def _open_edit_student_dialog(self, id_val: int):
        EditStudentDialog(self.parent, id_val, on_saved=self.refresh_student_list)

    def _open_enroll_face_dialog(self, id_val: int):
        from app.ui.registration_view import FaceRegistrationDialog
        FaceRegistrationDialog(self.parent, id_val, on_saved=self.refresh_student_list)


class AddStudentDialog(ctk.CTkToplevel):
    """Modal dialog for adding a new student."""

    def __init__(self, parent, on_saved: Optional[Callable] = None):
        super().__init__(parent)
        self.title("Add New Student")
        self.geometry("400x500")
        self.on_saved = on_saved
        self.grab_set()

        self._build_form()

    def _build_form(self):
        ctk.CTkLabel(self, text="Add New Student", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        self.stu_id_entry = ctk.CTkEntry(self, placeholder_text="Student ID (e.g. STU-101)", width=300)
        self.stu_id_entry.pack(pady=8)

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Full Name", width=300)
        self.name_entry.pack(pady=8)

        self.class_entry = ctk.CTkEntry(self, placeholder_text="Class (e.g. Class 12)", width=300)
        self.class_entry.pack(pady=8)

        self.section_entry = ctk.CTkEntry(self, placeholder_text="Section (e.g. A)", width=300)
        self.section_entry.pack(pady=8)

        self.roll_entry = ctk.CTkEntry(self, placeholder_text="Roll Number (Optional)", width=300)
        self.roll_entry.pack(pady=8)

        self.phone_entry = ctk.CTkEntry(self, placeholder_text="Phone Number (Optional)", width=300)
        self.phone_entry.pack(pady=8)

        self.err_label = ctk.CTkLabel(self, text="", text_color="red", font=ctk.CTkFont(size=12))
        self.err_label.pack(pady=5)

        ctk.CTkButton(self, text="Save Student", fg_color="green", width=300, command=self._save).pack(pady=15)

    def _save(self):
        sid = self.stu_id_entry.get()
        name = self.name_entry.get()
        cname = self.class_entry.get()
        sec = self.section_entry.get()
        roll = self.roll_entry.get()
        phone = self.phone_entry.get()

        try:
            add_student(sid, name, cname, sec, roll, phone)
            if self.on_saved:
                self.on_saved()
            self.destroy()
        except Exception as e:
            self.err_label.configure(text=str(e))


class EditStudentDialog(ctk.CTkToplevel):
    """Modal dialog for editing student details."""

    def __init__(self, parent, student_db_id: int, on_saved: Optional[Callable] = None):
        super().__init__(parent)
        self.title("Edit Student")
        self.geometry("400x520")
        self.student_db_id = student_db_id
        self.on_saved = on_saved
        self.grab_set()

        self.student_data = get_student_detail(student_db_id)
        self._build_form()

    def _build_form(self):
        ctk.CTkLabel(self, text="Edit Student Record", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        if not self.student_data:
            ctk.CTkLabel(self, text="Student record not found.", text_color="red").pack(pady=20)
            return

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Full Name", width=300)
        self.name_entry.pack(pady=8)
        self.name_entry.insert(0, self.student_data.get("name", ""))

        self.class_entry = ctk.CTkEntry(self, placeholder_text="Class", width=300)
        self.class_entry.pack(pady=8)
        self.class_entry.insert(0, self.student_data.get("class_name", ""))

        self.section_entry = ctk.CTkEntry(self, placeholder_text="Section", width=300)
        self.section_entry.pack(pady=8)
        self.section_entry.insert(0, self.student_data.get("section", ""))

        self.roll_entry = ctk.CTkEntry(self, placeholder_text="Roll Number", width=300)
        self.roll_entry.pack(pady=8)
        self.roll_entry.insert(0, self.student_data.get("roll_number") or "")

        self.phone_entry = ctk.CTkEntry(self, placeholder_text="Phone Number", width=300)
        self.phone_entry.pack(pady=8)
        self.phone_entry.insert(0, self.student_data.get("phone") or "")

        self.err_label = ctk.CTkLabel(self, text="", text_color="red", font=ctk.CTkFont(size=12))
        self.err_label.pack(pady=5)

        ctk.CTkButton(self, text="Update Record", width=300, command=self._update).pack(pady=15)

    def _update(self):
        name = self.name_entry.get()
        cname = self.class_entry.get()
        sec = self.section_entry.get()
        roll = self.roll_entry.get()
        phone = self.phone_entry.get()

        try:
            update_student_details(
                self.student_db_id,
                name=name,
                class_name=cname,
                section=sec,
                roll_number=roll,
                phone=phone,
            )
            if self.on_saved:
                self.on_saved()
            self.destroy()
        except Exception as e:
            self.err_label.configure(text=str(e))


class EnrollFaceDialog(ctk.CTkToplevel):
    """Modal dialog for enrolling student face data using image, video, or camera mode."""

    def __init__(self, parent, student_db_id: int, on_saved: Optional[Callable] = None):
        super().__init__(parent)
        self.title("Face Data Enrollment")
        self.geometry("450x420")
        self.student_db_id = student_db_id
        self.on_saved = on_saved
        self.grab_set()

        self.student_data = get_student_detail(student_db_id)
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="Student Face Enrollment", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        if not self.student_data:
            ctk.CTkLabel(self, text="Student record not found.", text_color="red").pack(pady=20)
            return

        name = self.student_data.get("name", "Unknown")
        code = self.student_data.get("student_id", "")
        status_str = self.student_data.get("face_data_status", "Pending")

        ctk.CTkLabel(self, text=f"Student: {name} ({code})", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        ctk.CTkLabel(self, text=f"Current Status: {status_str}", text_color="gray").pack(pady=2)

        # AI Runtime Model Availability Status
        from app.ai.config import get_ai_runtime_status
        ai_status = get_ai_runtime_status()
        status_color = "green" if ai_status["is_available"] else "orange"
        ctk.CTkLabel(
            self,
            text=f"AI Engine: {ai_status['status']}",
            text_color=status_color,
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(pady=8)

        self.info_label = ctk.CTkLabel(
            self,
            text="Provide sample image(s) or video to enroll student face.",
            wraplength=380,
            font=ctk.CTkFont(size=12),
        )
        self.info_label.pack(pady=10)

        # Mode Selection Buttons Frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)

        self.img_btn = ctk.CTkButton(
            btn_frame,
            text="Select Test Image File",
            width=180,
            command=self._enroll_from_image_file,
        )
        self.img_btn.pack(side="left", padx=5)

        self.cam_btn = ctk.CTkButton(
            btn_frame,
            text="Test Camera Capture",
            width=180,
            fg_color="gray",
            command=self._enroll_from_camera,
        )
        self.cam_btn.pack(side="left", padx=5)

        self.err_label = ctk.CTkLabel(self, text="", text_color="red", font=ctk.CTkFont(size=12), wraplength=380)
        self.err_label.pack(pady=10)

    def _enroll_from_image_file(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Face Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not file_path:
            return

        try:
            import cv2
            img = cv2.imread(file_path)
            if img is None:
                self.err_label.configure(text="Failed to load image file.")
                return

            from app.ai.enrollment import FaceEnrollmentManager
            manager = FaceEnrollmentManager()
            # Pass 5 sample copies of frame for enrollment
            res = manager.enroll_student_from_frames(self.student_db_id, [img] * 5)
            self.err_label.configure(text=f"Enrollment successful! (Samples used: {res['valid_samples_used']})", text_color="green")
            if self.on_saved:
                self.on_saved()
        except Exception as e:
            self.err_label.configure(text=f"Enrollment Error: {e}", text_color="red")

    def _enroll_from_camera(self):
        from app.ai.providers import CameraFrameProvider
        cam = CameraFrameProvider(camera_index=0)
        if not cam.is_available:
            self.err_label.configure(
                text="Camera Unavailable: No physical USB webcam detected on this PC. (Camera-less development mode active)",
                text_color="orange"
            )
            cam.release()
            return

        frames = []
        for _ in range(5):
            ret, frame = cam.get_frame()
            if ret and frame is not None:
                frames.append(frame)
        cam.release()

        if not frames:
            self.err_label.configure(text="Failed to capture frames from camera.", text_color="red")
            return

        try:
            from app.ai.enrollment import FaceEnrollmentManager
            manager = FaceEnrollmentManager()
            res = manager.enroll_student_from_frames(self.student_db_id, frames)
            self.err_label.configure(text="Camera enrollment successful!", text_color="green")
            if self.on_saved:
                self.on_saved()
        except Exception as e:
            self.err_label.configure(text=f"Camera Enrollment Error: {e}", text_color="red")
