"""
AI Configuration and Model Path Verification Module for AI-Enabled Smart Attendance System.
Handles model path validation and status reporting without performing any network/internet requests.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Dict, Tuple

from app.config import (
    FACE_DETECTION_MODEL_PATH,
    FACE_RECOGNITION_MODEL_PATH,
    FACE_MATCH_THRESHOLD,
    MODEL_IDENTIFIER,
    EMBEDDING_DIMENSION,
    MIN_FACE_SIZE,
)

logger = logging.getLogger(__name__)


class AIRuntimeStatus(Enum):
    AVAILABLE = "MODEL AVAILABLE"
    MISSING = "MODEL MISSING"
    LOAD_ERROR = "MODEL LOAD ERROR"


def check_models_exist() -> Tuple[bool, bool]:
    """
    Check local disk for presence of YuNet detector and SFace recognizer model files.
    Returns:
        Tuple[bool, bool]: (yunet_exists, sface_exists)
    """
    yunet_exists = FACE_DETECTION_MODEL_PATH.exists() and FACE_DETECTION_MODEL_PATH.stat().st_size > 0
    sface_exists = FACE_RECOGNITION_MODEL_PATH.exists() and FACE_RECOGNITION_MODEL_PATH.stat().st_size > 0
    return yunet_exists, sface_exists


def get_ai_runtime_status() -> Dict[str, any]:
    """
    Inspect local AI model status without accessing network.
    Returns structured status dictionary for UI and system diagnostics.
    """
    yunet_exists, sface_exists = check_models_exist()

    if not yunet_exists or not sface_exists:
        missing_models = []
        if not yunet_exists:
            missing_models.append(FACE_DETECTION_MODEL_PATH.name)
        if not sface_exists:
            missing_models.append(FACE_RECOGNITION_MODEL_PATH.name)
        
        status_msg = f"Missing model files: {', '.join(missing_models)}. Please run 'python scripts/download_models.py' during setup."
        logger.warning(f"AI Model Status: {AIRuntimeStatus.MISSING.value} - {status_msg}")
        
        return {
            "status": AIRuntimeStatus.MISSING.value,
            "is_available": False,
            "yunet_exists": yunet_exists,
            "sface_exists": sface_exists,
            "yunet_path": str(FACE_DETECTION_MODEL_PATH),
            "sface_path": str(FACE_RECOGNITION_MODEL_PATH),
            "message": status_msg,
        }

    return {
        "status": AIRuntimeStatus.AVAILABLE.value,
        "is_available": True,
        "yunet_exists": True,
        "sface_exists": True,
        "yunet_path": str(FACE_DETECTION_MODEL_PATH),
        "sface_path": str(FACE_RECOGNITION_MODEL_PATH),
        "message": "All required AI model files are available locally.",
    }
