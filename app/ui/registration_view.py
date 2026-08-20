"""
Dedicated CustomTkinter Student Face Registration UI Component for AI-Enabled Smart Attendance System.
Provides interactive sample collection, 5-sample progress counter, real-time quality feedback,
provider selection, re-registration confirmation, and de-registration controls.
"""

import logging
from typing import Callable, Optional, List, Dict, Any
import cv2
import numpy as np

try:
    import customtkinter as ctk
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

from app.students import (
    get_student_detail,
    register_student_face,
    reregister_student_face,
    deregister_student_face,
    get_student_registration_status,
)
from app.ai.config import get_ai_runtime_status
from app.ai.enrollment import FaceEnrollmentManager
from app.ai.providers import ImageFrameProvider, VideoFrameProvider, CameraFrameProvider

logger = logging.getLogger(__name__)


class FaceRegistrationDialog(ctk.CTkToplevel):
    """
    Modal dialog for acquiring 5 valid face samples and registering student biometric embeddings.
    """

    def __init__(self, parent, student_db_id: int, on_saved: Optional[Callable] = None):
        if not HAS_GUI:
            raise RuntimeError("CustomTkinter UI framework is not available.")

        super().__init__(parent)
        self.title("Student Face Registration")
        self.geometry("500x520")
        self.resizable(False, False)

        self.student_db_id = student_db_id
        self.on_saved = on_saved
        self.grab_set()

        self.enrollment_manager = FaceEnrollmentManager()
        self.captured_frames: List[np.ndarray] = []
        self.required_samples: int = 5

        self.student_info = get_student_detail(self.student_db_id)
        self.reg_status = get_student_registration_status(self.student_db_id)
        
        self._build_ui()

    def _build_ui(self):
        # Title Label
        ctk.CTkLabel(
            self,
            text="Biometric Face Registration",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=(15, 5))

        if not self.student_info:
            ctk.CTkLabel(self, text="Student record not found.", text_color="red").pack(pady=20)
            return

        # Student Details Card
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill="x", padx=20, pady=5)

        name = self.student_info.get("name", "Unknown")
        code = self.student_info.get("student_id", "")
        cname = self.student_info.get("class_name", "")
        sec = self.student_info.get("section", "")
        status_label = self.reg_status.get("status_label", "Pending")
        status_color = "green" if self.reg_status.get("is_enrolled") else "orange"

        ctk.CTkLabel(
            info_frame,
            text=f"{name} ({code}) — Class {cname}-{sec}",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(8, 2))

        ctk.CTkLabel(
            info_frame,
            text=f"Registration Status: {status_label}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=status_color,
        ).pack(anchor="w", padx=15, pady=(0, 8))

        # AI Runtime Engine Status
        ai_status = get_ai_runtime_status()
        engine_color = "green" if ai_status["is_available"] else "orange"
        ctk.CTkLabel(
            self,
            text=f"AI Engine: {ai_status['status']}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=engine_color,
        ).pack(pady=4)

        # Progress Counter & Bar Frame
        prog_frame = ctk.CTkFrame(self, fg_color="transparent")
        prog_frame.pack(fill="x", padx=25, pady=8)

        self.counter_label = ctk.CTkLabel(
            prog_frame,
            text=f"Valid Samples Captured: {len(self.captured_frames)} / {self.required_samples}",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.counter_label.pack(side="top", pady=2)

        self.progress_bar = ctk.CTkProgressBar(prog_frame, width=380)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(side="top", pady=4)

        # Quality Feedback Status Box
        self.feedback_label = ctk.CTkLabel(
            self,
            text="Ready to collect face samples. Choose input provider below.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            wraplength=420,
        )
        self.feedback_label.pack(pady=8)

        # Provider Controls Frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.img_btn = ctk.CTkButton(
            btn_frame,
            text="Select Image File",
            width=140,
            command=self._handle_image_provider,
        )
        self.img_btn.pack(side="left", padx=5)

        self.vid_btn = ctk.CTkButton(
            btn_frame,
            text="Select Video File",
            width=140,
            command=self._handle_video_provider,
        )
        self.vid_btn.pack(side="left", padx=5)

        self.cam_btn = ctk.CTkButton(
            btn_frame,
            text="Capture Webcam",
            width=140,
            fg_color="gray",
            command=self._handle_camera_provider,
        )
        self.cam_btn.pack(side="left", padx=5)

        # Bottom Actions Frame (De-register & Close)
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=20, pady=(15, 10))

        if self.reg_status.get("is_enrolled"):
            self.dereg_btn = ctk.CTkButton(
                bottom_frame,
                text="De-register Face Data",
                fg_color="red",
                hover_color="darkred",
                width=160,
                command=self._handle_deregister,
            )
            self.dereg_btn.pack(side="left", padx=5)

        self.close_btn = ctk.CTkButton(
            bottom_frame,
            text="Close",
            fg_color="gray",
            width=100,
            command=self.destroy,
        )
        self.close_btn.pack(side="right", padx=5)

    def _update_progress_display(self):
        count = len(self.captured_frames)
        self.counter_label.configure(text=f"Valid Samples Captured: {count} / {self.required_samples}")
        self.progress_bar.set(float(count) / float(self.required_samples))

    def _process_frame_sample(self, frame: np.ndarray) -> bool:
        """Validate sample quality and add to captured list if valid."""
        if len(self.captured_frames) >= self.required_samples:
            return False

        is_valid, msg, det = self.enrollment_manager.validate_frame_quality(frame)
        if not is_valid or det is None:
            self.feedback_label.configure(text=f"Sample Rejected: {msg}", text_color="orange")
            return False

        self.captured_frames.append(frame.copy())
        self._update_progress_display()
        self.feedback_label.configure(
            text=f"Sample {len(self.captured_frames)} / {self.required_samples} accepted! (Size: {det.bbox[2]}x{det.bbox[3]} px)",
            text_color="green",
        )

        if len(self.captured_frames) >= self.required_samples:
            self._finalize_enrollment()
        return True

    def _finalize_enrollment(self):
        """Complete 5-sample enrollment or re-enrollment."""
        try:
            if self.reg_status.get("is_enrolled"):
                res = reregister_student_face(self.student_db_id, self.captured_frames)
                action_msg = "Re-enrollment successful!"
            else:
                res = register_student_face(self.student_db_id, self.captured_frames)
                action_msg = "Face registration successful!"

            self.feedback_label.configure(
                text=f"{action_msg} 5 valid samples processed and 128D mean vector saved.",
                text_color="green",
            )
            if self.on_saved:
                self.on_saved()
        except Exception as e:
            self.feedback_label.configure(text=f"Enrollment Error: {e}", text_color="red")

    def _handle_image_provider(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Face Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")],
        )
        if not file_path:
            return

        try:
            provider = ImageFrameProvider(file_path)
            ret, frame = provider.get_frame()
            provider.release()

            if not ret or frame is None:
                self.feedback_label.configure(text="Failed to decode image file.", text_color="red")
                return

            # Submit frame sample
            self._process_frame_sample(frame)
        except Exception as e:
            self.feedback_label.configure(text=f"Image Error: {e}", text_color="red")

    def _handle_video_provider(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov")],
        )
        if not file_path:
            return

        try:
            provider = VideoFrameProvider(file_path)
            valid_added = 0
            while len(self.captured_frames) < self.required_samples:
                ret, frame = provider.get_frame()
                if not ret or frame is None:
                    break
                if self._process_frame_sample(frame):
                    valid_added += 1
            provider.release()

            if len(self.captured_frames) < self.required_samples:
                self.feedback_label.configure(
                    text=f"Video processing finished. Captured {len(self.captured_frames)} / {self.required_samples} valid samples. Please provide more frames.",
                    text_color="orange",
                )
        except Exception as e:
            self.feedback_label.configure(text=f"Video Error: {e}", text_color="red")

    def _handle_camera_provider(self):
        provider = CameraFrameProvider(camera_index=0)
        if not provider.is_available:
            self.feedback_label.configure(
                text="Camera Unavailable: No physical USB webcam detected on this development machine. (Camera-less mode active)",
                text_color="orange",
            )
            provider.release()
            return

        try:
            ret, frame = provider.get_frame()
            provider.release()
            if ret and frame is not None:
                self._process_frame_sample(frame)
            else:
                self.feedback_label.configure(text="Failed to capture frame from webcam.", text_color="red")
        except Exception as e:
            self.feedback_label.configure(text=f"Camera Error: {e}", text_color="red")

    def _handle_deregister(self):
        try:
            deregister_student_face(self.student_db_id)
            self.feedback_label.configure(text="Face registration deactivated successfully.", text_color="green")
            if self.on_saved:
                self.on_saved()
            self.destroy()
        except Exception as e:
            self.feedback_label.configure(text=f"De-registration failed: {e}", text_color="red")
