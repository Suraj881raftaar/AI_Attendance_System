"""
Camera Hardware FrameProvider implementation supporting live USB webcam streams with graceful missing-hardware fallback.
"""

import logging
from typing import Optional, Tuple
import cv2
import numpy as np

from app.ai.providers.base import FrameProvider

logger = logging.getLogger(__name__)


class CameraFrameProvider(FrameProvider):
    """
    FrameProvider for physical webcam devices with graceful error handling if hardware is absent.
    """

    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_available: bool = False
        self._initialize_camera()

    def _initialize_camera(self) -> None:
        """Attempt to open camera device index."""
        try:
            # On Windows, DirectShow backend (cv2.CAP_DSHOW) or default backend
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                # Fallback to default backend
                self.cap = cv2.VideoCapture(self.camera_index)

            if self.cap is not None and self.cap.isOpened():
                # Test reading a test frame to ensure physical presence
                ret, _ = self.cap.read()
                if ret:
                    self.is_available = True
                    logger.info(f"Camera device index {self.camera_index} initialized successfully.")
                else:
                    logger.warning(f"Camera device index {self.camera_index} opened but failed to capture test frame.")
                    self.release()
            else:
                logger.info(f"No physical camera detected at index {self.camera_index}.")
                self.release()
        except Exception as e:
            logger.warning(f"Exception during camera initialization for index {self.camera_index}: {e}")
            self.release()

    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Fetch live camera frame safely."""
        if not self.is_available or self.cap is None or not self.cap.isOpened():
            return False, None

        try:
            ret, frame = self.cap.read()
            if not ret or frame is None or frame.size == 0:
                return False, None
            return True, frame
        except Exception as e:
            logger.error(f"Error capturing frame from camera {self.camera_index}: {e}")
            return False, None

    def release(self) -> None:
        """Release camera hardware resource cleanly."""
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception as e:
                logger.warning(f"Error releasing camera {self.camera_index}: {e}")
            finally:
                self.cap = None
        self.is_available = False
