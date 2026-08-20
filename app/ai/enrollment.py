"""
Face Enrollment Business Workflow Module for AI-Enabled Smart Attendance System.
Handles multi-sample quality validation, feature vector averaging, session RBAC authorization, and database persistence.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import cv2
import numpy as np

from app.config import MODEL_IDENTIFIER, MIN_FACE_SIZE
from app.auth import get_session
from app.database import (
    get_student_by_id,
    create_or_update_face_data,
    deactivate_face_data,
)
from app.ai.detector import YuNetFaceDetector, FaceDetectionResult
from app.ai.embedder import SFaceRecognizer

logger = logging.getLogger(__name__)


def _require_authenticated_user() -> Dict[str, Any]:
    """Verify active user session, raising PermissionError if unauthenticated."""
    session = get_session()
    if not session.is_logged_in():
        raise PermissionError("Authentication required to perform face enrollment operations.")
    return session.get_current_user()  # type: ignore


class FaceEnrollmentManager:
    """
    Manages student face enrollment processing, quality checks, embedding generation, and DB persistence.
    """

    def __init__(
        self,
        detector: Optional[YuNetFaceDetector] = None,
        embedder: Optional[SFaceRecognizer] = None,
        db_path: Optional[Union[str, Path]] = None,
    ):
        self.detector = detector or YuNetFaceDetector()
        self.embedder = embedder or SFaceRecognizer()
        self.db_path = db_path

    def validate_frame_quality(
        self, frame: np.ndarray, min_face_size: Tuple[int, int] = MIN_FACE_SIZE, min_sharpness: float = 25.0
    ) -> Tuple[bool, str, Optional[FaceDetectionResult]]:
        """
        Validate face quality in a frame.
        
        Checks:
        1. Single face detected (rejects 0 or >1 faces)
        2. Bounding box size >= min_face_size (60x60)
        3. Image sharpness (Laplacian variance >= min_sharpness)
        """
        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
            return False, "Invalid or empty image frame.", None

        detections = self.detector.detect(frame)
        if len(detections) == 0:
            return False, "No face detected in frame.", None
        if len(detections) > 1:
            return False, f"Multiple faces ({len(detections)}) detected. Please ensure only one person is visible.", None

        det = detections[0]
        x, y, w, h = det.bbox

        if w < min_face_size[0] or h < min_face_size[1]:
            return False, f"Face bounding box ({w}x{h}) is too small. Minimum required is {min_face_size[0]}x{min_face_size[1]} pixels.", None

        # Crop face for sharpness check
        h_frame, w_frame, _ = frame.shape
        x2 = min(w_frame, x + w)
        y2 = min(h_frame, y + h)
        crop = frame[y:y2, x:x2]

        if crop.size > 0:
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            if sharpness < min_sharpness:
                return False, f"Image is too blurry (sharpness score {sharpness:.1f} < {min_sharpness}). Please hold still.", None

        return True, "Quality check passed.", det

    def enroll_student_from_frames(
        self,
        student_id: int,
        frames: List[np.ndarray],
        db_path: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """
        Enroll a student using a list of captured sample frames.
        
        :param student_id: Primary key ID of student.
        :param frames: List of BGR frame numpy arrays (recommended 5 samples).
        :param db_path: Optional SQLite database path override.
        :return: Dict containing enrollment result details.
        :raises PermissionError: If unauthenticated.
        :raises ValueError: If student inactive/not found or quality checks fail.
        """
        _require_authenticated_user()

        effective_db_path = db_path or self.db_path

        # Verify student existence and status
        student = get_student_by_id(student_id, db_path=effective_db_path)
        if not student:
            raise ValueError(f"Student with ID {student_id} does not exist.")
        if student.get("status") != "active":
            raise ValueError(f"Cannot enroll inactive student '{student['name']}' (ID {student_id}).")

        if not self.detector.is_loaded or not self.embedder.is_loaded:
            raise RuntimeError("AI model files are unavailable. Please verify models are installed locally.")

        if not frames or len(frames) == 0:
            raise ValueError("No frames provided for enrollment.")

        extracted_embeddings: List[np.ndarray] = []
        errors: List[str] = []

        for idx, frame in enumerate(frames):
            is_valid, msg, det = self.validate_frame_quality(frame)
            if not is_valid or det is None:
                errors.append(f"Sample {idx+1}: {msg}")
                continue

            feature = self.embedder.extract_feature(frame, det)
            if feature is not None:
                extracted_embeddings.append(feature)
            else:
                errors.append(f"Sample {idx+1}: Failed to extract feature vector.")

        if len(extracted_embeddings) == 0:
            error_details = "; ".join(errors) if errors else "No usable face samples passed validation."
            raise ValueError(f"Face enrollment failed: {error_details}")

        # Compute average feature embedding across valid samples
        mean_vector = np.mean(extracted_embeddings, axis=0)
        norm = np.linalg.norm(mean_vector)
        if norm > 0:
            mean_vector = mean_vector / norm

        # Serialize embedding as JSON string
        json_data = json.dumps(mean_vector.tolist())

        # Save to SQLite database
        record = create_or_update_face_data(
            student_id=student_id,
            model_identifier=MODEL_IDENTIFIER,
            encoding_data=json_data,
            data_format="json",
            db_path=effective_db_path,
        )

        logger.info(f"Successfully enrolled face data for student '{student['name']}' ({student['student_id']}) using {len(extracted_embeddings)} valid samples.")

        return {
            "success": True,
            "student_id": student_id,
            "student_code": student["student_id"],
            "student_name": student["name"],
            "valid_samples_used": len(extracted_embeddings),
            "total_samples_received": len(frames),
            "face_data_id": record["id"],
            "model_identifier": MODEL_IDENTIFIER,
        }

    def remove_enrollment(self, student_id: int, db_path: Optional[Union[str, Path]] = None) -> bool:
        """Deactivate face data for a student after authorization check."""
        _require_authenticated_user()
        effective_db_path = db_path or self.db_path
        return deactivate_face_data(student_id, db_path=effective_db_path)
