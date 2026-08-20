"""
Dedicated CustomTkinter Attendance View Component for AI-Enabled Smart Attendance System.
Provides live recognition stream display with green/red bounding box overlays,
activity feed log, today's attendance summary counters, and provider controls.
"""

import logging
import threading
import time
from typing import Optional, List, Dict, Any
import cv2
import numpy as np

try:
    import customtkinter as ctk
    from PIL import Image, ImageTk
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

from app.attendance.service import (
    process_recognition_frame,
    get_today_attendance_summary,
)
from app.ai.config import get_ai_runtime_status
from app.ai.providers import (
    FrameProvider,
    ImageFrameProvider,
    VideoFrameProvider,
    CameraFrameProvider,
)

logger = logging.getLogger(__name__)


class AttendanceViewFrame(ctk.CTkFrame):
    """
    Main Attendance Recognition UI View component.
    """

    def __init__(self, parent):
        if not HAS_GUI:
            raise RuntimeError("CustomTkinter UI framework is not available.")

        super().__init__(parent)

        self.current_provider: Optional[FrameProvider] = None
        self.is_streaming: bool = False
        self.stream_thread: Optional[threading.Thread] = None

        self._build_ui()
        self.refresh_summary_stats()

    def _build_ui(self):
        # Top Header & Summary Stats
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            header_frame,
            text="AI Attendance Recognition Engine",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        # Stats Cards Grid
        stats_grid = ctk.CTkFrame(header_frame, fg_color="transparent")
        stats_grid.pack(fill="x", padx=15, pady=5)

        self.card_total = self._create_stat_card(stats_grid, "TOTAL STUDENTS", "0", "gray")
        self.card_total.pack(side="left", expand=True, fill="both", padx=5)

        self.card_present = self._create_stat_card(stats_grid, "PRESENT TODAY", "0", "green")
        self.card_present.pack(side="left", expand=True, fill="both", padx=5)

        self.card_absent = self._create_stat_card(stats_grid, "ABSENT TODAY", "0", "orange")
        self.card_absent.pack(side="left", expand=True, fill="both", padx=5)

        self.card_pct = self._create_stat_card(stats_grid, "ATTENDANCE %", "0.0%", "blue")
        self.card_pct.pack(side="left", expand=True, fill="both", padx=5)

        # Middle Content: Left (Video Display Canvas), Right (Controls & Activity Feed)
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Left Column: Stream Display Canvas
        left_col = ctk.CTkFrame(content_frame)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # AI Status Bar above display
        ai_status = get_ai_runtime_status()
        ai_color = "green" if ai_status["is_available"] else "orange"
        self.status_banner = ctk.CTkLabel(
            left_col,
            text=f"AI Engine: {ai_status['status']} | Cosine Threshold: 0.363",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ai_color,
        )
        self.status_banner.pack(anchor="w", padx=15, pady=8)

        self.canvas_label = ctk.CTkLabel(
            left_col,
            text="No active frame stream.\nSelect provider (Image / Video / Camera) to start.",
            font=ctk.CTkFont(size=14),
            width=540,
            height=360,
            fg_color="black",
            text_color="gray",
        )
        self.canvas_label.pack(fill="both", expand=True, padx=10, pady=10)

        # Right Column: Controls & Activity Feed
        right_col = ctk.CTkFrame(content_frame, width=320)
        right_col.pack(side="right", fill="both", padx=(5, 0))

        # Provider Selector Frame
        prov_frame = ctk.CTkFrame(right_col)
        prov_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            prov_frame,
            text="Input Frame Provider",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(8, 4))

        self.img_mode_btn = ctk.CTkButton(
            prov_frame,
            text="Recognize Image File",
            command=self._start_image_mode,
        )
        self.img_mode_btn.pack(fill="x", padx=10, pady=4)

        self.vid_mode_btn = ctk.CTkButton(
            prov_frame,
            text="Stream Video File",
            command=self._start_video_mode,
        )
        self.vid_mode_btn.pack(fill="x", padx=10, pady=4)

        self.cam_mode_btn = ctk.CTkButton(
            prov_frame,
            text="Start USB Webcam",
            fg_color="gray",
            command=self._start_camera_mode,
        )
        self.cam_mode_btn.pack(fill="x", padx=10, pady=4)

        self.mobile_mode_btn = ctk.CTkButton(
            prov_frame,
            text="Mobile Camera (TEST)",
            fg_color="purple",
            hover_color="darkpurple",
            command=self._start_mobile_mode,
        )
        self.mobile_mode_btn.pack(fill="x", padx=10, pady=4)

        self.stop_btn = ctk.CTkButton(
            prov_frame,
            text="Stop Stream",
            fg_color="red",
            hover_color="darkred",
            state="disabled",
            command=self.stop_stream,
        )
        self.stop_btn.pack(fill="x", padx=10, pady=(4, 8))

        # Real-time Activity Feed
        feed_frame = ctk.CTkFrame(right_col)
        feed_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        ctk.CTkLabel(
            feed_frame,
            text="Real-time Activity Feed",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(8, 4))

        self.feed_textbox = ctk.CTkTextbox(feed_frame, height=200, font=ctk.CTkFont(size=11, family="Consolas"))
        self.feed_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        self.feed_textbox.configure(state="disabled")

        self.log_activity("System initialized. Ready for recognition stream.")

    def _create_stat_card(self, parent, title: str, val: str, color_theme: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(parent)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=10, weight="bold"), text_color="gray").pack(pady=(6, 0))
        lbl = ctk.CTkLabel(card, text=val, font=ctk.CTkFont(size=18, weight="bold"))
        lbl.pack(pady=(0, 6))
        card.value_label = lbl  # type: ignore
        return card

    def refresh_summary_stats(self):
        try:
            summary = get_today_attendance_summary()
            self.card_total.value_label.configure(text=str(summary["total_students"]))  # type: ignore
            self.card_present.value_label.configure(text=str(summary["present_count"]))  # type: ignore
            self.card_absent.value_label.configure(text=str(summary["absent_count"]))  # type: ignore
            self.card_pct.value_label.configure(text=f"{summary['attendance_percentage']}%")  # type: ignore
        except Exception as e:
            logger.warning(f"Failed to refresh summary stats: {e}")

    def log_activity(self, message: str):
        self.feed_textbox.configure(state="normal")
        self.feed_textbox.insert("end", f"{message}\n")
        self.feed_textbox.see("end")
        self.feed_textbox.configure(state="disabled")

    def _display_bgr_frame(self, frame: np.ndarray):
        """Render OpenCV BGR frame onto CustomTkinter canvas label."""
        if frame is None or frame.size == 0:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)

        # Scale image to fit canvas label bounds nicely
        cw = max(320, self.canvas_label.winfo_width())
        ch = max(240, self.canvas_label.winfo_height())
        img.thumbnail((cw, ch), Image.Resampling.LANCZOS)

        img_tk = ImageTk.PhotoImage(image=img)
        self.canvas_label.configure(image=img_tk, text="")
        self.canvas_label.image = img_tk  # Keep reference

    def _start_image_mode(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Image File for Recognition",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")],
        )
        if not file_path:
            return

        self.stop_stream()
        try:
            provider = ImageFrameProvider(file_path)
            ret, frame = provider.get_frame()
            provider.release()

            if ret and frame is not None:
                annotated_frame, events = process_recognition_frame(frame, mark_attendance=True)
                self._display_bgr_frame(annotated_frame)

                for ev in events:
                    self.log_activity(f"[{ev['timestamp']}] {ev['message']}")

                self.refresh_summary_stats()
            else:
                self.log_activity("Error: Failed to decode image file.")
        except Exception as e:
            self.log_activity(f"Image Recognition Error: {e}")

    def _start_video_mode(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Video File for Recognition Stream",
            filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov")],
        )
        if not file_path:
            return

        self.stop_stream()
        try:
            self.current_provider = VideoFrameProvider(file_path)
            self._start_stream_thread()
        except Exception as e:
            self.log_activity(f"Video Stream Error: {e}")

    def _start_camera_mode(self):
        self.stop_stream()
        cam = CameraFrameProvider(camera_index=0)
        if not cam.is_available:
            self.log_activity("Camera Unavailable: No physical USB webcam detected on this dev PC.")
            cam.release()
            return

        self.current_provider = cam
        self._start_stream_thread()

    def _start_mobile_mode(self):
        from customtkinter import CTkInputDialog
        from app.ai.providers import MobileCameraFrameProvider

        dialog = CTkInputDialog(
            text="Enter Mobile Phone Camera Stream URL:\n(e.g. http://192.168.1.100:8080/video)",
            title="Mobile Camera (TEST)",
        )
        stream_url = dialog.get_input()
        if not stream_url:
            return

        self.stop_stream()
        try:
            mob = MobileCameraFrameProvider(stream_url=stream_url)
            if not mob.is_available:
                self.log_activity(f"Mobile Camera Error: Unreachable or invalid stream URL ({stream_url}).")
                mob.release()
                return

            self.current_provider = mob
            self._start_stream_thread()
        except Exception as e:
            self.log_activity(f"Mobile Camera Stream Exception: {e}")

    def _start_stream_thread(self):
        self.is_streaming = True
        self.stop_btn.configure(state="normal")
        self.stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.stream_thread.start()

    def _stream_loop(self):
        self.log_activity("Stream started...")
        while self.is_streaming and self.current_provider:
            ret, frame = self.current_provider.get_frame()
            if not ret or frame is None:
                break

            try:
                annotated, events = process_recognition_frame(frame, mark_attendance=True)
                self.after(0, self._display_bgr_frame, annotated)

                for ev in events:
                    if ev.get("status") in ("attendance_created", "unknown", "inactive_rejected"):
                        self.after(0, self.log_activity, f"[{ev['timestamp']}] {ev['message']}")

                self.after(0, self.refresh_summary_stats)
            except Exception as e:
                logger.error(f"Frame processing error: {e}")

            time.sleep(0.05)  # Cap loop rate to ~20 FPS

        self.after(0, self.log_activity, "Stream finished.")
        self.after(0, self.stop_stream)

    def stop_stream(self):
        self.is_streaming = False
        if self.current_provider:
            self.current_provider.release()
            self.current_provider = None

        if HAS_GUI:
            self.stop_btn.configure(state="disabled")
