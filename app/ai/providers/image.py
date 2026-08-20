"""
Static Image FrameProvider implementation for camera-less testing and single-image inference.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple, Union
import cv2
import numpy as np

from app.ai.providers.base import FrameProvider

logger = logging.getLogger(__name__)


class ImageFrameProvider(FrameProvider):
    """
    FrameProvider that yields frames from a static image file or existing numpy BGR array.
    """

    def __init__(self, source: Union[str, Path, np.ndarray]):
        self._frame: Optional[np.ndarray] = None
        self._served: bool = False

        if isinstance(source, np.ndarray):
            if source.size == 0 or len(source.shape) != 3:
                raise ValueError("Invalid numpy image array provided.")
            self._frame = source.copy()
        else:
            path_str = str(source)
            if not Path(path_str).exists():
                raise FileNotFoundError(f"Image file not found: {path_str}")
            image = cv2.imread(path_str)
            if image is None:
                raise ValueError(f"Failed to decode image file: {path_str}")
            self._frame = image

    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Return the loaded image frame."""
        if self._frame is None:
            return False, None
        return True, self._frame.copy()

    def release(self) -> None:
        """Clear image memory."""
        self._frame = None
        self._served = True
