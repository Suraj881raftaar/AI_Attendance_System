# AI Engine & Mathematical Model Explanation

## 1. Overview of AI Architecture

The AI-Enabled Smart Attendance System utilizes lightweight, CPU-optimized deep neural network (DNN) models operating locally via OpenCV DNN (`cv2.dnn`).

```text
Input Video Frame (BGR) ──> YuNet Face Detector ──> Cropped Face & Landmarks ──> SFace Recognizer ──> 128D Feature Vector ──> Cosine Matcher (>= 0.363)
```

---

## 2. Face Detection: YuNet Architecture

- **Model File**: `face_detection_yunet_2023mar.onnx`
- **Input Resolution**: Flexible (Default $640 \times 480$ or original frame dimensions)
- **Mechanism**: YuNet is an ultra-lightweight convolutional neural network (CNN) designed specifically for real-time edge CPU face detection.
- **Output**: For each detected face, YuNet outputs a 14-element array:
  - Bounding box coordinates $[x, y, w, h]$
  - 5 facial landmark points (Right eye, Left eye, Nose tip, Right mouth corner, Left mouth corner) $[x_1, y_1, \dots, x_5, y_5]$
  - Detection confidence score $c \in [0.0, 1.0]$ (Filtered by $c \ge 0.60$)

---

## 3. Feature Embedding: SFace Architecture

- **Model File**: `face_recognition_sface_2021dec.onnx`
- **Input**: $112 \times 112$ aligned facial crop with landmark normalization.
- **Output**: 128-dimensional floating-point feature embedding vector $\mathbf{v} \in \mathbb{R}^{128}$.
- **Vector Normalization**: The output vector is normalized using $L_2$ norm:
  $$\hat{\mathbf{v}} = \frac{\mathbf{v}}{\|\mathbf{v}\|_2} = \frac{\mathbf{v}}{\sqrt{\sum_{i=1}^{128} v_i^2}}$$

---

## 4. Face Matching: Cosine Similarity Metric

To identify whether a query face $\mathbf{q}$ matches an enrolled student template $\mathbf{e}$, the system computes the Cosine Similarity metric $S_{\cos}$:

$$S_{\cos}(\mathbf{q}, \mathbf{e}) = \frac{\mathbf{q} \cdot \mathbf{e}}{\|\mathbf{q}\|_2 \|\mathbf{e}\|_2}$$

Since both vectors are $L_2$-normalized ($\|\mathbf{q}\|_2 = \|\mathbf{e}\|_2 = 1.0$), the cosine similarity simplifies to the dot product:

$$S_{\cos}(\mathbf{q}, \mathbf{e}) = \sum_{i=1}^{128} q_i \cdot e_i$$

---

## 5. Recognition Decision Rule & Threshold

The system compares $S_{\cos}$ against the fixed Cosine Similarity threshold `FACE_MATCH_THRESHOLD = 0.363`:

$$\text{Decision} = \begin{cases} \text{Recognized (Student ID)}, & \text{if } \max (S_{\cos}) \ge 0.363 \\ \text{Unknown Face}, & \text{if } \max (S_{\cos}) < 0.363 \end{cases}$$

---

## 6. Safety Cooldown & Anti-Hallucination Controls

1. **10-Second Cooldown**: After a student is recognized, a 10-second timestamp buffer prevents repeated processing of the same face across consecutive video frames.
2. **Database Unique Protection**: SQLite enforces `UNIQUE(student_id, attendance_date)`, preventing duplicate attendance inserts on the same day even if the cooldown expires.
3. **Unknown Rejection**: Unenrolled or unrecognized faces ($S_{\cos} < 0.363$) are labeled as "Unknown" without triggering attendance creation or false match errors.
