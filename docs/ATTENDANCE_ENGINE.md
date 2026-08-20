# AI Attendance Engine Architecture & Recognition Workflow

## 1. Executive Architecture Overview

The **AI Attendance Engine** automatically identifies registered students in live or recorded video/image streams using local computer vision AI models and records daily attendance in a local SQLite database (`attendance` table).

### End-to-End Recognition Workflow
```text
Frame Stream Input (Webcam / Video / Image Provider)
        ↓
YuNet Face Detection (Dynamic Bounding Boxes)
        ↓
SFace 128D Feature Extraction & L2 Normalization
        ↓
Cosine Similarity Matcher (Threshold >= 0.363)
        ↓
Match Decision Logic:
├── Similarity < 0.363 -> UNKNOWN FACE (Red Box) -> Logged in Activity Feed, ZERO DB Records Created
└── Similarity >= 0.363 -> RECOGNIZED STUDENT (Green Box)
        ↓
Validation Rules for Recognized Student:
├── Is Student Active? (If Inactive -> Reject & Log "Inactive student rejected", NO Attendance Created)
├── Inside 10s Cooldown? (If Yes -> Skip Duplicate Stream Overhead)
└── Already Marked Present Today? (If Yes -> Log "Already marked Present today")
        ↓
Passes All Rules -> CREATE Present Attendance Record (Date: YYYY-MM-DD, Time: HH:MM:SS, Method: 'automatic')
        ↓
Update UI Summary Statistics Cards & Real-Time Activity Event Log
```

---

## 2. Confidence Threshold & Duplicate Rules

- **Centralized Confidence Threshold**: Centrally configured at `FACE_MATCH_THRESHOLD = 0.363` in `app/config.py`.
- **10-Second Cooldown**: In-memory timestamp dictionary prevents duplicate processing overhead during continuous video stream rendering.
- **Database Duplicate Protection**: SQLite `attendance` table enforces `UNIQUE (student_id, attendance_date)`. Maximum of 1 automatic `Present` record per student per date (`YYYY-MM-DD`).

---

## 3. Unknown Faces & Inactive Protection

- **Unknown Faces**: Rendered with red bounding boxes and labeled `UNKNOWN (Score)`. Unknown faces NEVER create attendance records, student records, or face-data records in SQLite.
- **Inactive Students**: If a face matches a student whose status is `inactive` in SQLite, attendance is rejected and logged as `Inactive student rejected`.

---

## 4. Camera-less Development Mode

The development PC operates cleanly without physical webcam hardware through three frame providers:
1. `ImageFrameProvider`: Processes static test image files.
2. `VideoFrameProvider`: Streams frames from pre-recorded MP4/AVI files.
3. `CameraFrameProvider`: Attempts webcam access; auto-detects missing camera hardware gracefully without crashing.
