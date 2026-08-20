# Student Face Registration & Biometric Management Documentation

## 1. System Overview

The **Student Face Registration System** connects student academic records with AI biometric face representations in local SQLite database storage.

### Core Workflow
```text
Select Active Student
        ↓
Open Face Registration Window
        ↓
Select Input Provider (Image / Video / Camera)
        ↓
Capture Frame Sample
        ↓
Quality Validation Checks:
  - Single Face Present
  - Bounding Box Size >= 60x60 px
  - Laplacian Variance Sharpness >= 25.0
        ↓
Extract 128D SFace Feature Vector & L2 Normalize
        ↓
Repeat until 5 Valid Samples Collected (0/5 -> 5/5)
        ↓
Compute 128D Mean Vector across 5 Samples & L2 Normalize
        ↓
Serialize as JSON String Array
        ↓
Save to SQLite face_data Table (model_identifier='opencv_sface_v1')
        ↓
Update Student UI Status Badge (Enrolled)
```

---

## 2. Real-time Quality Checks & Thresholds

Every submitted frame sample must satisfy 3 strict criteria:
1. **Single Face Rule**: Exactly 1 face detected by YuNet. Multi-face or zero-face frames are rejected with explicit user feedback messages ("No face detected", "Multiple faces detected").
2. **Minimum Face Size**: Face bounding box width and height must be $\ge 60 \times 60$ pixels. Smaller faces trigger "Face too small, please move closer".
3. **Sharpness Threshold**: Crop Laplacian variance must be $\ge 25.0$. Blurry frames trigger "Image is too blurry".

---

## 3. Transactional Re-Enrollment & De-Registration

- **Re-Enrollment**: Authorized users can re-enroll a student. Transactional safety guarantees that if new sample collection or extraction fails, the existing active face registration record is PRESERVED UNTOUCHED.
- **De-Registration**: Deactivates a student's face data (`status='inactive'`) while preserving all historical student information and past attendance logs intact.

---

## 4. Security & Biometric Privacy Model

- **100% Local Storage**: Feature embeddings stored in local SQLite `face_data` table.
- **Zero Image Retention**: Raw frame images are processed entirely in memory (RAM) and discarded. No facial photos are written to disk or committed to Git.
- **Backend RBAC Authorization**: `_require_authenticated_user()` checks enforced at the service layer for all enrollment, re-enrollment, and de-registration APIs.
- **Camera-less Fallback**: Application functions seamlessly without physical camera hardware.
