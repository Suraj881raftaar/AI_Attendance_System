# STAGE 4 — OFFLINE AI IMPLEMENTATION DOCUMENTATION

## 1. Overview & Architecture

Stage 4 implements a 100% local, offline, CPU-first face recognition system for the AI-Enabled Smart Attendance System.
The module relies natively on OpenCV DNN ONNX runtime (`opencv-python-headless==5.0.0.93`), utilizing **YuNet** for face detection and **SFace** for 128-dimensional face embedding feature extraction.

### Core Stack
- **Face Detector**: YuNet (`cv2.FaceDetectorYN`) | Model: `face_detection_yunet_2023mar.onnx` (~230 KB)
- **Face Recognizer**: SFace (`cv2.FaceRecognizerSF`) | Model: `face_recognition_sface_2021dec.onnx` (~38.7 MB)
- **Matching Engine**: Cosine Similarity ($\ge 0.363$ threshold)
- **Database Storage**: SQLite `face_data` table (`encoding_data` stored as 128D float JSON string array)
- **Inference Mode**: 100% Local / Offline / CPU-Only (Zero GPU, Zero CUDA, Zero Cloud API dependency)

---

## 2. Decoupled Frame Provider System (Camera-Less Abstraction)

To ensure development, testing, and application execution work on PCs without physical camera hardware, frame acquisition is decoupled via the `FrameProvider` abstract class:

1. **`ImageFrameProvider`**: Reads static image files or numpy arrays.
2. **`VideoFrameProvider`**: Reads pre-recorded video streams frame-by-frame via `cv2.VideoCapture`.
3. **`CameraFrameProvider`**: Interacts with physical USB webcams (`camera_index=0`). If no camera hardware is present, it auto-detects unavailability and gracefully yields `(False, None)` without crashing the application.

---

## 3. Local Model Policy & Developer Setup

Runtime execution MUST NEVER access the internet or perform automatic downloads. Model files are managed strictly through a separate setup script:

- **Developer Setup Script**: `python scripts/download_models.py`
- **Canonical Model Path**:
  - `models/face_detection/face_detection_yunet_2023mar.onnx` (SHA256: `8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4`)
  - `models/face_recognition/face_recognition_sface_2021dec.onnx` (SHA256: `0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79`)
- **License**: OpenCV Open Source (Apache 2.0)

If model files are missing at runtime, the application logs a `MODEL MISSING` status and displays setup instructions without attempting any network calls or throwing uncaught exceptions.

---

## 4. Student Face Enrollment Workflow

1. Authenticated teacher/admin session starts enrollment (`FaceEnrollmentManager`).
2. Validates frame quality:
   - Minimum face bounding box size ($60 \times 60$ px).
   - Single face enforcement (rejects multi-face frames).
   - Laplacian variance sharpness check ($\ge 25.0$).
3. Captures 5 valid face samples.
4. Extracts 128D embedding vectors, computes L2-normalized mean feature vector.
5. Serializes mean vector as JSON array and persists in `face_data` table under `model_identifier='opencv_sface_v1'`.

---

## 5. Face Recognition & Safety Rules

1. **YuNet Detection**: Identifies all visible faces in a frame.
2. **SFace Feature Extraction**: Computes 128D normalized feature vector for each face.
3. **Database Matcher**: Compares against enrolled active students using Cosine Similarity. Matches with score $\ge 0.363$ return student identification.
4. **Safety & Duplicate Prevention**:
   - Detection alone never marks attendance.
   - 10-second in-memory cooldown per student ID prevents rapid duplicate hits.
   - Integrates with database `check_duplicate_attendance` (1 record per student per day rule).
   - Rejects inactive student records automatically.
