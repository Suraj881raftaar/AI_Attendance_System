"""
Abstract FrameProvider hierarchy for camera-decoupled frame acquisition.
Allows AI inference to process frames identically from static images, pre-recorded video, or webcams.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple
import numpy as np


class FrameProvider(ABC):
    """
    Abstract Base Class for frame acquisition providers.
    """

    @abstractmethod
    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Fetch the next frame.
        
        Returns:
            Tuple[bool, Optional[np.ndarray]]:
                - success (bool): True if frame was retrieved successfully.
                - frame (Optional[np.ndarray]): BGR OpenCV image matrix or None.
        """
        pass

    @abstractmethod
    def release(self) -> None:
        """
        Release underlying video stream, image buffer, or hardware camera resources.
        """
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
