"""
Developer & Installation Model Downloader Script for AI-Enabled Smart Attendance System.

Run this script during project setup to download required pretrained ONNX models:
- YuNet Face Detection (face_detection_yunet_2023mar.onnx)
- SFace Face Recognition (face_recognition_sface_2021dec.onnx)

RUNTIME APPLICATION WILL NOT ACCESS THE INTERNET AT RUNTIME.
"""

import os
import sys
import hashlib
import logging
from pathlib import Path
import urllib.request

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("model_downloader")

# Root directory setup
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
YUNET_DIR = MODELS_DIR / "face_detection"
SFACE_DIR = MODELS_DIR / "face_recognition"

YUNET_PATH = YUNET_DIR / "face_detection_yunet_2023mar.onnx"
SFACE_PATH = SFACE_DIR / "face_recognition_sface_2021dec.onnx"

YUNET_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
SFACE_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"

EXPECTED_YUNET_SIZE = 232589
EXPECTED_SFACE_SIZE = 38696353


def compute_sha256(filepath: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def download_file(url: str, dest_path: Path, expected_size: int) -> bool:
    """Download a file with progress reporting and size validation."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Downloading {dest_path.name} from {url}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        actual_size = dest_path.stat().st_size
        if actual_size != expected_size:
            logger.warning(f"Downloaded file size ({actual_size} bytes) does not match expected size ({expected_size} bytes).")
        sha256 = compute_sha256(dest_path)
        logger.info(f"Successfully saved to {dest_path} (Size: {actual_size} bytes, SHA256: {sha256})")
        return True
    except Exception as e:
        logger.error(f"Failed to download {dest_path.name}: {e}")
        return False


def main():
    logger.info("Starting developer AI model setup process...")
    YUNET_DIR.mkdir(parents=True, exist_ok=True)
    SFACE_DIR.mkdir(parents=True, exist_ok=True)

    success = True
    if not YUNET_PATH.exists() or YUNET_PATH.stat().st_size != EXPECTED_YUNET_SIZE:
        if not download_file(YUNET_URL, YUNET_PATH, EXPECTED_YUNET_SIZE):
            success = False
    else:
        logger.info(f"YuNet model already present: {YUNET_PATH} (SHA256: {compute_sha256(YUNET_PATH)})")

    if not SFACE_PATH.exists() or SFACE_PATH.stat().st_size != EXPECTED_SFACE_SIZE:
        if not download_file(SFACE_URL, SFACE_PATH, EXPECTED_SFACE_SIZE):
            success = False
    else:
        logger.info(f"SFace model already present: {SFACE_PATH} (SHA256: {compute_sha256(SFACE_PATH)})")

    if success:
        logger.info("AI model setup completed successfully. All models are available locally.")
        sys.exit(0)
    else:
        logger.error("AI model setup encountered errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
