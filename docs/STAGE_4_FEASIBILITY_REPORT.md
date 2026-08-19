# STAGE 4 FEASIBILITY REPORT

PROJECT:
AI-Enabled Smart Attendance System (Class 12 Academic Project)

HARDWARE:
- CPU: Intel(R) Core(TM) i3-12100 (4 Physical Cores / 8 Logical Processors @ 3.30 GHz - 4.30 GHz)
- RAM: 12 GB Physical Memory (11.72 GB usable)
- GPU: Intel(R) UHD Graphics 730 (Integrated Graphics)

OPERATING SYSTEM:
Windows 10 Pro 64-bit (10.0.19045 AMD64)

PYTHON VERSION:
Python 3.13.14 64-bit

CAMERA STATUS:
NO CAMERA AVAILABLE (Current PC has no webcam connected)

AI OPTIONS EVALUATED:

OPTION 1: OpenCV YuNet (Detector) + SFace (Embedder) ONNX Models
- Detection: YuNet (`cv2.dnn_FaceDetectorYN`) (~230 KB ONNX weight)
- Recognition: SFace (`cv2.dnn_FaceRecognizerSF`) (~36 MB ONNX weight, 128D vectors)
- Python 3.13 / Windows Status: 100% compatible natively via `opencv-python` (v5.0+). Zero C++ build tools required.
- Performance: ~5-10ms detection, ~15-25ms feature extraction per face on Intel Core i3-12100 CPU.
- Rating: EXCELLENT (Primary Recommendation).

OPTION 2: OpenCV Haar Cascade + LBPH (Local Binary Patterns Histograms)
- Detection: Haar Cascade (`haarcascade_frontalface_default.xml`)
- Recognition: OpenCV LBPH (`cv2.face.LBPHFaceRecognizer`)
- Python 3.13 / Windows Status: 100% compatible.
- Performance: Very fast CPU execution, but sensitive to lighting variations and head angles.
- Rating: GOOD (Fallback Recommendation).

OPTION 3: `face_recognition` (dlib C++ wrapper)
- Python 3.13 / Windows Status: INCOMPATIBLE / HIGH RISK. Prebuilt PyPI wheels for Python 3.13 on 64-bit Windows do not exist. Requires MSVC C++ CMake compilation environment.
- Rating: REJECTED due to Windows + Python 3.13 build failures.

OPTION 4: DeepFace / TensorFlow / Keras
- Python 3.13 / Windows Status: Heavyweight (1.5GB+ dependencies). Native Python 3.13 Windows wheels incomplete.
- Rating: REJECTED.

PRIMARY RECOMMENDATION:
OpenCV YuNet (Face Detector) + OpenCV SFace (128D Deep Feature Embedder). Native ONNX execution via `opencv-python`.

FALLBACK:
OpenCV Haar Cascade + LBPH (Local Binary Patterns Histograms).

FACE DETECTION:
YuNet ONNX model (`cv2.dnn_FaceDetectorYN`). Real-time bounding box detection, eye/nose/mouth landmark detection, and confidence scoring.

FACE RECOGNITION:
SFace ONNX model (`cv2.dnn_FaceRecognizerSF`). Extracts 128-dimensional L2-normalized floating-point feature embedding vectors.

MODEL:
- Detector Model: YuNet (`face_detection_yunet_2023mar.onnx`, ~230 KB)
- Recognizer Model: SFace (`face_recognition_sface_2021dec.onnx`, ~36 MB)
- License: Open Source (BSD / Apache 2.0 compatible)

EMBEDDING STRATEGY:
128-element float array serialized as a JSON string `"[0.123, -0.456, ...]"` stored in the existing `face_data.encoding_data` column. Matching computed using Cosine Similarity ($\text{Threshold} \ge 0.363$).

CAMERA ARCHITECTURE:
Decoupled `FrameProvider` abstract base class (`app/ai/providers/base.py`). Supports `CameraFrameProvider` (Webcam), `ImageFrameProvider` (Static files), and `VideoFrameProvider` (Prerecorded video). AI engine operates on BGR NumPy array frames.

NO-CAMERA DEVELOPMENT:
Fully supported via `ImageFrameProvider` and `VideoFrameProvider`. Allows full AI detection, embedding generation, database integration, threshold tuning, and automated testing on camera-less PCs using test image datasets.

PERFORMANCE EXPECTATION:
- Frame Latency: ~25-35 ms per frame total on Intel i3-12100 CPU.
- Frame Rate: ~30 FPS CPU processing for 720p frames.
- Memory Footprint: ~150 MB RAM for model weights and OpenCV runtime.

DEPENDENCIES:
- `opencv-python` (v5.0.0.93 - Already installed in project `venv`)
- `numpy` (v2.5.2 - Already installed in project `venv`)
- Zero new third-party package installations required.

PYTHON COMPATIBILITY:
100% compatible with Python 3.13.14 64-bit on Windows.

WINDOWS COMPATIBILITY:
100% compatible with Windows 10/11 64-bit. Prebuilt binaries included in `opencv-python`.

OFFLINE CAPABILITY:
100% offline. Models run locally on CPU without internet connections or cloud APIs.

DATABASE IMPACT:
Zero schema changes required. Uses existing Stage 1 `face_data` table structure: `student_id`, `model_identifier` ('opencv_sface_v1'), `encoding_data` (JSON array string).

PRIVACY DESIGN:
Raw face images captured during enrollment are processed in RAM to extract 128D vectors and immediately discarded. Raw face pictures are never saved to disk, stored in the database, or committed to Git.

SECURITY RISKS:
- Photo Spoofing: Medium risk (Standard 2D camera limitation). Mitigated in academic context by documentation.
- Embedding Tampering: Low risk (Protected by SQLite database and user authentication).

ANTI-SPOOFING:
Basic 2D webcams cannot perform hardware depth anti-spoofing. For Class 12 academic project scope, anti-spoofing limitations will be documented clearly in presentation materials.

TESTING STRATEGY:
- Automated tests (`tests/test_stage4_ai.py`) using synthetic/test image fixtures.
- Test detection accuracy, embedding extraction, cosine similarity thresholds, unknown face rejection, and multiple face handling without camera hardware.

COST:
$0 (Uses existing hardware, standard library, and open-source models).

IMPLEMENTATION PLAN:
- 4A: Package ONNX model files (`yunet.onnx`, `sface.onnx`) into `app/ai/models/`.
- 4B: Implement `FrameProvider` hierarchy (`Image`, `Video`, `Camera`).
- 4C: Implement `YuNetFaceDetector` and `SFaceEmbedder`.
- 4D: Implement `FaceMatcher` Cosine Similarity engine.
- 4E: Implement `StudentFaceEnrollment` workflow (5-sample quality check & averaging).
- 4F: Implement Live Recognition Engine for Attendance.
- 4G: Build Stage 4 pytest suite (`tests/test_stage4_ai.py`).

KNOWN LIMITATIONS:
- Development PC has no webcam; live camera testing requires plugging in an external USB webcam.
- Extreme low light or steep face angles (>45 degrees) reduce detection confidence.

FINAL RECOMMENDATION:
APPROVE Stage 4 Architecture. Proceed to Stage 4 Implementation upon explicit user approval.
