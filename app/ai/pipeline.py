"""
End-to-End AI Recognition Pipeline Module for AI-Enabled Smart Attendance System.
Coordinates FrameProvider, Face Detector, Embedder, Matcher, Safety Cooldown, and Attendance Recording.
"""

import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import cv2
import numpy as np

from app.config import FACE_MATCH_THRESHOLD, MIN_FACE_SIZE
from app.database import create_attendance, check_duplicate_attendance, get_student_by_id
from app.ai.config import get_ai_runtime_status
from app.ai.detector import YuNetFaceDetector, FaceDetectionResult
from app.ai.embedder import SFaceRecognizer
from app.ai.matcher import FaceMatcher, MatchResult
from app.ai.providers import FrameProvider

logger = logging.getLogger(__name__)


class AIRecognitionPipeline:
    """
    High-level orchestrator for real-time and offline face recognition processing.
    """

    def __init__(
        self,
        detector: Optional[YuNetFaceDetector] = None,
        embedder: Optional[SFaceRecognizer] = None,
        matcher: Optional[FaceMatcher] = None,
        threshold: float = FACE_MATCH_THRESHOLD,
        cooldown_seconds: float = 10.0,
        db_path: Optional[Union[str, Path]] = None,
    ):
        self.detector = detector or YuNetFaceDetector()
        self.embedder = embedder or SFaceRecognizer()
        self.matcher = matcher or FaceMatcher(embedder=self.embedder, threshold=threshold, db_path=db_path)
        self.threshold = threshold
        self.cooldown_seconds = cooldown_seconds
        self.db_path = db_path
        
        # Cooldown map: {student_id: last_recognition_timestamp}
        self._last_recognized: Dict[int, float] = {}

    def is_operational(self) -> bool:
        """Check if AI runtime models are loaded and ready."""
        return self.detector.is_loaded and self.embedder.is_loaded

    def process_frame(
        self,
        frame: Optional[np.ndarray],
        enrolled_cache: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[List[MatchResult], np.ndarray]:
        """
        Process a single image frame: detect faces, extract embeddings, match against DB, and draw bounding boxes.
        
        :param frame: BGR image numpy array.
        :param enrolled_cache: Optional cached enrolled embeddings list.
        :return: Tuple[List[MatchResult], np.ndarray] (match results list, annotated frame copy).
        """
        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
            return [], np.zeros((100, 100, 3), dtype=np.uint8)

        annotated_frame = frame.copy()

        if not self.is_operational():
            # Draw warning overlay on annotated frame
            cv2.putText(
                annotated_frame,
                "AI Models Not Available",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )
            return [], annotated_frame

        # Run face detection
        detections = self.detector.detect(frame)
        if not detections:
            return [], annotated_frame

        # Load enrolled database embeddings once if cache not provided
        if enrolled_cache is None:
            enrolled_cache = self.matcher.load_enrolled_embeddings(db_path=self.db_path)

        results: List[MatchResult] = []

        for det in detections:
            x, y, w, h = det.bbox

            # Skip undersized face bounding boxes
            if w < MIN_FACE_SIZE[0] or h < MIN_FACE_SIZE[1]:
                continue

            # Extract 128D embedding
            feature = self.embedder.extract_feature(frame, det)
            if feature is None:
                continue

            # Perform matching against database
            match = self.matcher.match_embedding(
                query_embedding=feature,
                bbox=det.bbox,
                enrolled_cache=enrolled_cache,
                db_path=self.db_path,
            )
            results.append(match)

            # Draw visual annotation on frame
            if match.is_known:
                color = (0, 255, 0)  # Green for recognized known student
                label = f"{match.student_name} ({match.similarity_score:.2f})"
            else:
                color = (0, 0, 255)  # Red for unknown face
                label = f"Unknown ({match.similarity_score:.2f})"

            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(
                annotated_frame,
                label,
                (x, max(20, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )

        return results, annotated_frame

    def mark_attendance_from_match(
        self,
        match: MatchResult,
        recognition_method: str = "automatic",
        db_path: Optional[Union[str, Path]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Record attendance for a recognized student after passing safety & cooldown checks.
        
        :param match: MatchResult object from recognition.
        :param recognition_method: 'automatic' or 'manual'.
        :param db_path: Optional SQLite database path.
        :return: Attendance dict if recorded, None if skipped due to unknown/cooldown/duplicate.
        """
        if not match.is_known or match.student_id is None:
            return None

        student_id = match.student_id
        now = time.time()
        effective_db = db_path or self.db_path

        # 1. Cooldown check
        last_time = self._last_recognized.get(student_id, 0.0)
        if now - last_time < self.cooldown_seconds:
            logger.debug(f"Skipping attendance for student ID {student_id}: inside cooldown window ({self.cooldown_seconds}s).")
            return None

        # 2. Verify active student status
        student = get_student_by_id(student_id, db_path=effective_db)
        if not student or student.get("status") != "active":
            logger.warning(f"Cannot record attendance for inactive or missing student ID {student_id}.")
            return None

        # 3. Check duplicate attendance for today
        today_date = datetime.now().strftime("%Y-%m-%d")
        if check_duplicate_attendance(student_id, today_date, db_path=effective_db):
            logger.info(f"Attendance already recorded today for student '{student['name']}' ({student['student_id']}).")
            self._last_recognized[student_id] = now
            return None

        # 4. Record attendance
        current_time = datetime.now().strftime("%H:%M:%S")
        try:
            record = create_attendance(
                student_id=student_id,
                attendance_date=today_date,
                attendance_time=current_time,
                status="Present",
                recognition_method=recognition_method,
                confidence_score=match.similarity_score,
                db_path=effective_db,
            )
            self._last_recognized[student_id] = now
            logger.info(f"Attendance recorded for '{student['name']}' ({student['student_id']}) at {current_time} (Confidence: {match.similarity_score:.3f}).")
            return record
        except Exception as e:
            logger.error(f"Failed to record attendance for student ID {student_id}: {e}")
            return None
