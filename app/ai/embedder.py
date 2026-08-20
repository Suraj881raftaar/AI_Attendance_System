"""
SFace Deep Feature Extraction and Embedding Module for AI-Enabled Smart Attendance System.
Uses OpenCV DNN FaceRecognizerSF to extract 128D facial feature vectors and compute similarity metrics.
"""

import logging
from pathlib import Path
from typing import Optional, Union
import cv2
import numpy as np

from app.config import FACE_RECOGNITION_MODEL_PATH, EMBEDDING_DIMENSION
from app.ai.detector import FaceDetectionResult

logger = logging.getLogger(__name__)


class SFaceRecognizer:
    """
    Local face recognizer and feature extractor using OpenCV's SFace ONNX model (cv2.FaceRecognizerSF).
    """

    def __init__(self, model_path: Optional[Union[str, Path]] = None):
        self.model_path = Path(model_path) if model_path else FACE_RECOGNITION_MODEL_PATH
        self._recognizer: Optional[cv2.FaceRecognizerSF] = None
        self.is_loaded: bool = False
        self._load_model()

    def _load_model(self) -> None:
        """Initialize cv2.FaceRecognizerSF if model file exists on local disk."""
        if not self.model_path.exists() or self.model_path.stat().st_size == 0:
            logger.warning(f"SFace model missing at path: {self.model_path}")
            self.is_loaded = False
            return

        try:
            self._recognizer = cv2.FaceRecognizerSF.create(
                model=str(self.model_path),
                config="",
                backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
                target_id=cv2.dnn.DNN_TARGET_CPU,
            )
            self.is_loaded = True
            logger.info("SFace recognizer model initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to load SFace recognizer model: {e}")
            self._recognizer = None
            self.is_loaded = False

    def align_crop(self, frame: np.ndarray, detection: Union[FaceDetectionResult, np.ndarray]) -> Optional[np.ndarray]:
        """
        Align and crop face region using SFace alignCrop.
        
        :param frame: BGR image frame.
        :param detection: FaceDetectionResult object or raw YuNet detection array row.
        :return: Aligned face crop numpy array (112x112 BGR) or None on failure.
        """
        if not self.is_loaded or self._recognizer is None:
            self._load_model()
            if not self.is_loaded or self._recognizer is None:
                return None

        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
            return None

        raw_det = detection.raw_detection if isinstance(detection, FaceDetectionResult) else detection
        if raw_det is None or not isinstance(raw_det, np.ndarray):
            return None

        try:
            aligned_face = self._recognizer.alignCrop(frame, raw_det)
            return aligned_face
        except Exception as e:
            logger.error(f"Error aligning face crop: {e}")
            return None

    def extract_feature(self, frame: np.ndarray, detection: Union[FaceDetectionResult, np.ndarray]) -> Optional[np.ndarray]:
        """
        Align face and extract 128-dimensional normalized feature vector.
        
        :param frame: BGR image frame.
        :param detection: FaceDetectionResult object or raw YuNet detection array row.
        :return: 128D float32 numpy array or None on failure.
        """
        aligned_face = self.align_crop(frame, detection)
        if aligned_face is None:
            return None

        try:
            feature = self._recognizer.feature(aligned_face)
            if feature is None or feature.size != EMBEDDING_DIMENSION:
                logger.error(f"Extracted feature has invalid dimensions: {feature.shape if feature is not None else None}")
                return None

            # Flatten to 1D array of 128 float32 values
            feature_1d = feature.flatten().astype(np.float32)

            # Ensure L2 normalization
            norm = np.linalg.norm(feature_1d)
            if norm > 0:
                feature_1d = feature_1d / norm

            return feature_1d
        except Exception as e:
            logger.error(f"Error extracting SFace feature vector: {e}")
            return None

    def compute_cosine_similarity(self, feature1: np.ndarray, feature2: np.ndarray) -> float:
        """
        Calculate Cosine Similarity between two 128D feature vectors.
        
        :param feature1: 128D numpy array.
        :param feature2: 128D numpy array.
        :return: Cosine similarity score [-1.0 to 1.0].
        """
        if feature1 is None or feature2 is None:
            return 0.0

        f1 = feature1.flatten()
        f2 = feature2.flatten()

        if len(f1) != EMBEDDING_DIMENSION or len(f2) != EMBEDDING_DIMENSION:
            return 0.0

        if self.is_loaded and self._recognizer is not None:
            try:
                # Use SFace match method
                score = self._recognizer.match(
                    f1.reshape(1, -1),
                    f2.reshape(1, -1),
                    cv2.FACE_RECOGNIZER_SF_FR_COSINE
                )
                return float(score)
            except Exception as e:
                logger.debug(f"SFace match API call fallback to numpy dot product: {e}")

        # Fallback numpy cosine similarity calculation: (u . v) / (|u| * |v|)
        norm1 = np.linalg.norm(f1)
        norm2 = np.linalg.norm(f2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(np.dot(f1, f2) / (norm1 * norm2))
