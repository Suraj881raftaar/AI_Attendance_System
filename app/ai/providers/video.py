"""
Pre-recorded Video FrameProvider implementation for offline testing and video file processing.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple, Union
import cv2
import numpy as np

from app.ai.providers.base import FrameProvider

logger = logging.getLogger(__name__)


class VideoFrameProvider(FrameProvider):
    """
    FrameProvider that yields frames sequentially from a video file via OpenCV VideoCapture.
    """

    def __init__(self, video_path: Union[str, Path], loop: bool = False):
        self.video_path = str(video_path)
        self.loop = loop
        
        if not Path(self.video_path).exists():
            raise FileNotFoundError(f"Video file not found: {self.video_path}")
            
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Failed to open video file: {self.video_path}")

    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read next frame from video file."""
        if self.cap is None or not self.cap.isOpened():
            return False, None

        ret, frame = self.cap.read()
        if not ret:
            if self.loop:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    return False, None
            else:
                return False, None

        return True, frame

    def release(self) -> None:
        """Release VideoCapture handle."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
