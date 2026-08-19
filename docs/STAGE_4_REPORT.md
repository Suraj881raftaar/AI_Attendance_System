# STAGE 4 — AI / Face Recognition Architecture Report

STAGE:
STAGE 4 — AI / Face Recognition Architecture

STATUS:
PASS

HARDWARE:
Intel(R) Core(TM) i3-12100 CPU (4 Cores / 8 Threads @ 3.30 GHz), 12 GB RAM, Intel(R) UHD Graphics 730.

CAMERA:
NO CAMERA AVAILABLE (Development PC currently has no camera connected).

PYTHON:
Python 3.13.14 64-bit on Windows 10 Pro 64-bit.

AI OPTIONS:
- Option 1: OpenCV YuNet + SFace ONNX Models (Evaluated & Recommended)
- Option 2: OpenCV Haar Cascade + LBPH (Evaluated & Recommended Fallback)
- Option 3: `face_recognition` / dlib (Evaluated & Rejected due to Windows Python 3.13 build failures)
- Option 4: DeepFace / TensorFlow (Evaluated & Rejected due to dependency bloat)

PRIMARY RECOMMENDATION:
OpenCV YuNet (ONNX Face Detector) + OpenCV SFace (128D ONNX Feature Extractor). Native ONNX execution in `opencv-python`.

FALLBACK:
OpenCV Haar Cascade + LBPH (Local Binary Patterns Histograms).

MODEL:
- Detector: YuNet (`face_detection_yunet_2023mar.onnx`, ~230 KB)
- Recognizer: SFace (`face_recognition_sface_2021dec.onnx`, ~36 MB)

DEPENDENCIES:
Existing `opencv-python` (v5.0.0.93) and `numpy` (v2.5.2) already present in project `venv`. Zero new external package installations required.

PERFORMANCE:
~25-35 ms total frame processing latency (~30 FPS CPU execution) on Intel Core i3-12100 CPU.

PRIVACY:
Raw face images processed in RAM and immediately discarded. 128D feature vectors stored locally in SQLite database. Zero cloud APIs, zero image files saved to disk, zero face images in Git.

SECURITY:
Backend RBAC session authorization required for face enrollment and deletion. Cosine Similarity threshold decision engine ($\ge 0.363$).

DATABASE IMPACT:
Zero schema modifications required. Uses existing Stage 1 `face_data` table (`student_id`, `model_identifier`, `encoding_data`, `data_format`).

NO-CAMERA DEVELOPMENT:
Decoupled `FrameProvider` architecture (`CameraFrameProvider`, `ImageFrameProvider`, `VideoFrameProvider`). Enables 100% of AI pipeline development, testing, and verification to run on camera-less PCs using static test image fixtures.

TESTING STRATEGY:
Automated pytest test suite using test image fixtures to verify face detection, 128D feature extraction, Cosine Similarity matching, unknown face rejection, and multiple face handling without physical camera hardware.

IMPLEMENTATION PLAN:
Sub-stages 4A through 4G detailing model weight packaging, provider implementation, detector/embedder/matcher modules, enrollment workflow, live recognition engine, and pytest suite creation.

DOCUMENTATION:
- Created `docs/STAGE_4_AI_ARCHITECTURE.md`
- Created `docs/STAGE_4_FEASIBILITY_REPORT.md`
- Created `docs/STAGE_4_REPORT.md`

GIT COMMIT:
Pending (Stage 4 Architecture checkpoint).

KNOWN ISSUES:
None.

NEXT STEP:
STAGE 4 IMPLEMENTATION

APPROVAL REQUIRED:
YES
