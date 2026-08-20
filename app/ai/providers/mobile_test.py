"""
Mobile Phone Camera Test Adapter for AI-Enabled Smart Attendance System.
Enables local network video streaming (e.g. HTTP/MJPEG/RTSP stream from an Android camera app)
for testing the AI recognition pipeline without physical USB webcam hardware.

TEST-ONLY COMPONENT: Does NOT modify production AI architecture or database.
"""

import logging
from typing import Tuple, Optional
import cv2
import numpy as np

from app.ai.providers.base import FrameProvider

logger = logging.getLogger(__name__)


class MobileCameraFrameProvider(FrameProvider):
    """
    Frame provider adapter for streaming video over local Wi-Fi from a mobile phone camera.
    Uses cv2.VideoCapture with a configurable HTTP/RTSP stream URL.
    """

    def __init__(self, stream_url: str = ""):
        self.stream_url = stream_url.strip()
        self.cap: Optional[cv2.VideoCapture] = None
        self._is_available: bool = False

        if self.stream_url:
            self._connect()

    def _connect(self):
        """Attempt connection to mobile video stream URL."""
        try:
            logger.info(f"Connecting to mobile stream URL: {self.stream_url}")
            self.cap = cv2.VideoCapture(self.stream_url)
            if self.cap.isOpened():
                # Read initial test frame to verify stream validity
                ret, frame = self.cap.read()
                if ret and frame is not None and frame.size > 0:
                    self._is_available = True
                    logger.info("Mobile camera stream connected successfully.")
                else:
                    logger.warning("Mobile stream opened but failed to yield initial frame.")
                    self.release()
            else:
                logger.warning(f"Could not open mobile stream at URL: {self.stream_url}")
                self.release()
        except Exception as e:
            logger.error(f"Mobile camera stream connection error: {e}")
            self.release()

    @property
    def is_available(self) -> bool:
        """Check if mobile camera stream is connected and operational."""
        return self._is_available and self.cap is not None and self.cap.isOpened()

    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read the next video frame from the mobile camera stream.

        :return: Tuple[bool, Optional[np.ndarray]] (success flag, BGR frame array or None).
        """
        if not self.is_available or self.cap is None:
            return False, None

        try:
            ret, frame = self.cap.read()
            if ret and frame is not None and frame.size > 0:
                return True, frame
            else:
                logger.warning("Failed to read frame from mobile camera stream.")
                return False, None
        except Exception as e:
            logger.error(f"Error reading mobile camera frame: {e}")
            return False, None

    def release(self) -> None:
        """Release mobile camera VideoCapture resource cleanly."""
        self._is_available = False
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception as e:
                logger.warning(f"Error releasing mobile VideoCapture: {e}")
            self.cap = None
