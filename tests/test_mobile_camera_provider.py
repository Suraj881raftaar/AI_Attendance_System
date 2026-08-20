"""
Automated Test Suite for Mobile Phone Camera Test Adapter.
Tests provider initialization, stream URL configuration, invalid URL handling,
unreachable connection fallback, resource release, and FrameProvider interface compliance.

DOES NOT REQUIRE AN ACTUAL PHONE CONNECTED. MOCKS/FAKES USED FOR NETWORK CAPTURE.
"""

from unittest.mock import MagicMock, patch
import numpy as np
import pytest

from app.ai.providers.base import FrameProvider
from app.ai.providers.mobile_test import MobileCameraFrameProvider


def test_mobile_provider_inheritance():
    """Verify MobileCameraFrameProvider inherits from FrameProvider abstraction."""
    assert issubclass(MobileCameraFrameProvider, FrameProvider)


def test_mobile_provider_empty_url():
    """Verify provider with empty stream URL initializes gracefully as unavailable."""
    provider = MobileCameraFrameProvider(stream_url="")
    assert provider.is_available is False

    ret, frame = provider.get_frame()
    assert ret is False
    assert frame is None

    provider.release()
    assert provider.is_available is False


def test_mobile_provider_unreachable_url():
    """Verify provider handling of unreachable stream URL (e.g. invalid port/IP)."""
    unreachable_url = "http://127.0.0.1:59999/video"
    provider = MobileCameraFrameProvider(stream_url=unreachable_url)

    assert provider.is_available is False

    ret, frame = provider.get_frame()
    assert ret is False
    assert frame is None

    provider.release()


def test_mobile_provider_mocked_successful_stream():
    """Test frame retrieval interface using mocked cv2.VideoCapture."""
    mock_frame = np.full((240, 320, 3), 128, dtype=np.uint8)

    with patch("cv2.VideoCapture") as mock_cap_class:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, mock_frame)
        mock_cap_class.return_value = mock_cap

        provider = MobileCameraFrameProvider(stream_url="http://192.168.1.100:8080/video")

        assert provider.is_available is True

        ret, frame = provider.get_frame()
        assert ret is True
        assert frame is not None
        assert frame.shape == (240, 320, 3)

        provider.release()
        assert provider.is_available is False
        mock_cap.release.assert_called_once()


def test_mobile_provider_connection_failure_during_read():
    """Test handling of stream disconnection during active read."""
    with patch("cv2.VideoCapture") as mock_cap_class:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        # First read succeeds (initial connection check), second read fails (stream dropped)
        mock_cap.read.side_effect = [(True, np.zeros((100, 100, 3), dtype=np.uint8)), (False, None)]
        mock_cap_class.return_value = mock_cap

        provider = MobileCameraFrameProvider(stream_url="http://192.168.1.100:8080/video")
        assert provider.is_available is True

        ret, frame = provider.get_frame()
        assert ret is False
        assert frame is None

        provider.release()
