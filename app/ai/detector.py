"""
YuNet Face Detection Wrapper Module for AI-Enabled Smart Attendance System.
Uses OpenCV DNN FaceDetectorYN for fast local face detection.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, Union
import cv2
import numpy as np

from app.config import FACE_DETECTION_MODEL_PATH

logger = logging.getLogger(__name__)


@dataclass
class FaceDetectionResult:
    """
    Structured container for face detection outputs.
    """
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float
    landmarks: Tuple[Tuple[int, int], ...]  # 5 facial landmarks: (right_eye, left_eye, nose, right_mouth, left_mouth)
    raw_detection: np.ndarray  # Raw detection row from YuNet for SFace alignCrop


class YuNetFaceDetector:
    """
    Local face detector using OpenCV's YuNet ONNX model (cv2.FaceDetectorYN).
    """

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        score_threshold: float = 0.6,
        nms_threshold: float = 0.3,
        top_k: int = 5000,
    ):
        self.model_path = Path(model_path) if model_path else FACE_DETECTION_MODEL_PATH
        self.score_threshold = score_threshold
        self.nms_threshold = nms_threshold
        self.top_k = top_k
        self._detector: Optional[cv2.FaceDetectorYN] = None
        self._current_input_size: Tuple[int, int] = (300, 300)
        self.is_loaded: bool = False
        self._load_model()

    def _load_model(self) -> None:
        """Initialize cv2.FaceDetectorYN if model file exists on local disk."""
        if not self.model_path.exists() or self.model_path.stat().st_size == 0:
            logger.warning(f"YuNet model missing at path: {self.model_path}")
            self.is_loaded = False
            return

        try:
            # Create FaceDetectorYN instance
            self._detector = cv2.FaceDetectorYN.create(
                model=str(self.model_path),
                config="",
                input_size=self._current_input_size,
                score_threshold=self.score_threshold,
                nms_threshold=self.nms_threshold,
                top_k=self.top_k,
                backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
                target_id=cv2.dnn.DNN_TARGET_CPU,
            )
            self.is_loaded = True
            logger.info("YuNet face detector initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to load YuNet face detector model: {e}")
            self._detector = None
            self.is_loaded = False

    def detect(self, frame: Optional[np.ndarray]) -> List[FaceDetectionResult]:
        """
        Detect faces in a BGR image frame.
        
        :param frame: BGR image numpy array.
        :return: List of FaceDetectionResult objects. Empty list if frame invalid or no faces found.
        """
        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0 or len(frame.shape) != 3:
            return []

        if not self.is_loaded or self._detector is None:
            # Re-attempt lazy load in case file was placed after initialization
            self._load_model()
            if not self.is_loaded or self._detector is None:
                return []

        h, w, _ = frame.shape
        if (w, h) != self._current_input_size:
            self._current_input_size = (w, h)
            try:
                self._detector.setInputSize((w, h))
            except Exception as e:
                logger.error(f"Failed to set YuNet input size to {(w, h)}: {e}")
                return []

        try:
            faces = self._detector.detect(frame)
            if faces is None or len(faces) <= 1 or faces[1] is None:
                return []

            results: List[FaceDetectionResult] = []
            detections_matrix = faces[1]

            for face in detections_matrix:
                # YuNet output layout:
                # [0:4]  bbox (x, y, w, h)
                # [4:14] 5 landmarks (x, y for right_eye, left_eye, nose, right_mouth, left_mouth)
                # [14]   confidence score
                bbox_x = max(0, int(face[0]))
                bbox_y = max(0, int(face[1]))
                bbox_w = int(face[2])
                bbox_h = int(face[3])
                confidence = float(face[14])

                landmarks = (
                    (int(face[4]), int(face[5])),    # right eye
                    (int(face[6]), int(face[7])),    # left eye
                    (int(face[8]), int(face[9])),    # nose tip
                    (int(face[10]), int(face[11])),  # right mouth corner
                    (int(face[12]), int(face[13])),  # left mouth corner
                )

                results.append(
                    FaceDetectionResult(
                        bbox=(bbox_x, bbox_y, bbox_w, bbox_h),
                        confidence=confidence,
                        landmarks=landmarks,
                        raw_detection=face,
                    )
                )

            return results
        except Exception as e:
            logger.error(f"Error during YuNet face detection: {e}")
            return []
