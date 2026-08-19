# STAGE 4 — AI & Face Recognition Master Architecture

## 1. Executive Summary

This document specifies the master architecture for the **AI & Face Recognition Module** (`app/ai/`) of the AI-Enabled Smart Attendance System. 

The architecture is specifically engineered to run on standard Windows PC hardware (CPU-bound) using Python 3.13, with **full support for camera-less development** via decoupled frame providers.

---

## 2. Hardware & Runtime Constraints

- **Development Hardware**: Intel Core i3-12100 CPU (4 Cores / 8 Threads @ ~3.30GHz - 4.30GHz), 12 GB RAM, Intel UHD Graphics 730.
- **Operating System**: Windows 10 (64-bit AMD64).
- **Python Version**: Python 3.13.14 (64-bit).
- **Camera Availability**: **NO CAMERA CONNECTED** on current development PC.
- **Inference Mode**: 100% local, CPU-based execution. Zero cloud API calls. Zero GPU dependencies.

---

## 3. Decoupled Frame Provider Architecture (Camera Abstraction)

To ensure development, testing, and demonstration can proceed on PCs without physical webcams, frame acquisition is decoupled from AI inference using an abstract `FrameProvider` hierarchy.

```text
                        +----------------------+
                        |    FrameProvider     | (Abstract Base Class)
                        +----------------------+
                                   |
           +-----------------------+-----------------------+
           |                       |                       |
+--------------------+   +-------------------+   +--------------------+
| CameraFrameProvider|   | ImageFrameProvider|   | VideoFrameProvider |
+--------------------+   +-------------------+   +--------------------+
 (Webcam / USB Dev)      (Single / Batch File)   (Prerecorded Video)
```

### Interface Definition
```python
class FrameProvider(ABC):
    @abstractmethod
    def get_frame(() -> Tuple[bool, Optional[np.ndarray]]:
        """Return (success, bgr_image_frame_numpy_array)."""
        pass

    @abstractmethod
    def release(self) -> None:
        """Release underlying camera or file handles."""
        pass
```

### Execution Modes
- **Mode A (No-Camera Development & Testing)**: Uses `ImageFrameProvider` and `VideoFrameProvider` to read test images/videos from disk. The application auto-detects missing camera hardware and seamlessly falls back to static file mode without crashing.
- **Mode B (Live Production Camera)**: Uses OpenCV `cv2.VideoCapture(index)` via `CameraFrameProvider` when a physical webcam is plugged in.

---

## 4. Recommended AI Model Stack

### 4.1 Primary Recommendation: OpenCV YuNet + SFace (ONNX Deep Neural Networks)
- **Face Detector**: `YuNet` (`cv2.dnn_FaceDetectorYN`). Fast ONNX face detector (~230 KB weight size). Detects faces in 5–10 ms on CPU.
- **Face Embedder & Recognizer**: `SFace` (`cv2.dnn_FaceRecognizerSF`). 128-dimensional deep feature extractor (~36 MB weight size). Computes 128D normalized feature vector in 15–25 ms on CPU.
- **Python 3.13 / Windows Compatibility**: Native support built directly into `opencv-python` (v5.0+ / v4.8+). **Zero external C++ compilation or build tools required**.
- **Distance Metric**: Cosine Similarity ($D_{cos}$) and L2 Euclidean Distance ($D_{L2}$).
  $$\text{Cosine Similarity}(u, v) = \frac{u \cdot v}{\|u\| \|v\|}$$
- **Matching Threshold**: Default Cosine Similarity threshold $\ge 0.363$ (configurable via `application_settings`).

### 4.2 Fallback Recommendation: OpenCV Haar Cascade + LBPH
- **Face Detector**: `Haar Cascade` (`haarcascade_frontalface_default.xml`).
- **Face Recognizer**: Local Binary Patterns Histograms (`cv2.face.LBPHFaceRecognizer_create`).
- **Use Case**: Emergency zero-model-download offline fallback.

---

## 5. AI Recognition Pipeline Flow

```text
[Frame Input (BGR)]
       ↓
[Frame Validation (Check resolution & format)]
       ↓
[Face Detection (YuNet)] ───► (No faces found: Return Unknown/Empty)
       ↓
[Face Quality & Minimum Size Check (min 60x60 px)]
       ↓
[Face Alignment & Cropping (SFace alignCrop)]
       ↓
[128D Embedding Feature Extraction (SFace feature)]
       ↓
[Compare against Enrolled Database Embeddings]
       ↓
[Compute Cosine Similarity Scores]
       ↓
[Highest Score >= Threshold (0.363)] ──► YES ──► Match Recognized (Student ID)
       │
       ▼ NO
[Mark as Unknown Face]
```

---

## 6. Student Face Enrollment Workflow (Stage 4 Design)

1. **User Action**: Teacher selects a student record in the UI and clicks "Enroll Face Data".
2. **Sample Collection**: Capture 5 distinct face samples (frontal, slight left turn, slight right turn, slight tilt, varied expression).
3. **Quality Validation**: Each sample must pass:
   - Minimum face bounding box size ($60 \times 60$ pixels).
   - Single face detection check (reject frames with multiple faces).
   - Sharpness/blur check (Laplacian variance threshold).
4. **Feature Vector Averaging**: Extract 128D embedding vector for each of the 5 samples, normalize, and calculate the mean vector.
5. **Database Storage**: Serialize the mean 128D vector as a JSON array (`"[0.123, -0.456, ...]"`), store in `face_data.encoding_data` with `model_identifier = 'opencv_sface_v1'`.
6. **Privacy Cleanup**: Discard all temporary image buffers from RAM immediately.

---

## 7. Multiple Face & Anti-Spoofing Design

- **Multiple Faces**: The detector identifies all visible face bounding boxes in a frame. The engine processes each face independently, matching against enrolled embeddings.
- **Anti-Spoofing Policy**: 
  - For a Class 12 academic desktop project, high-complexity active liveness (IR depth sensors / flash reflection) is not feasible on standard USB webcams.
  - A lightweight passive challenge (e.g., requiring a slight head movement or eye blink prompt during enrollment) can be optionally evaluated.
  - System limitations will be clearly documented in academic presentation materials.

---

## 8. Database Integration Strategy

Uses the existing Stage 1 `face_data` table without schema modifications:
```sql
CREATE TABLE IF NOT EXISTS face_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    model_identifier TEXT NOT NULL,      -- e.g. 'opencv_sface_v1'
    encoding_data TEXT NOT NULL,         -- JSON array of 128 floats
    data_format TEXT NOT NULL DEFAULT 'json',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
);
```

---

## 9. Proposed Module Structure

```text
app/ai/
├── __init__.py
├── detector.py          # YuNet Face Detector wrapper
├── embedder.py          # SFace 128D Feature Extractor
├── matcher.py           # Cosine Similarity decision engine
├── pipeline.py          # End-to-end recognition pipeline
├── models/
│   ├── .gitkeep
│   ├── yunet.onnx       # YuNet detector model (Stage 4)
│   └── sface.onnx       # SFace embedding model (Stage 4)
└── providers/
    ├── base.py          # Abstract FrameProvider
    ├── camera.py        # USB / Webcam provider
    ├── image.py         # Static image file provider
    └── video.py         # Video file provider
```

---

## 10. Security & Privacy Model

- **Local Storage Only**: All feature vectors remain in local SQLite (`data/attendance.db`).
- **No Cloud Transmission**: Zero network requests to third-party AI APIs.
- **No Raw Image Retention**: Images are processed in memory and discarded. Raw face pictures are never committed to Git repository.
- **Access Control**: Enrollment and face data deactivation require authenticated sessions.
