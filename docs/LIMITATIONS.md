# System Boundaries & Technical Limitations

## 1. Executive Summary

This document formally declares the technical boundaries, physical hardware constraints, and environmental limitations of the AI-Enabled Smart Attendance System.

---

## 2. Technical & Environmental Limitations

1. **Lighting & Illumination Sensitivity**:
   - The YuNet face detector requires minimum ambient illumination. Extreme low light (under 10 lux) or harsh backlighting (direct sun facing camera) may lower detection confidence score below the $0.60$ threshold.
2. **Pose & Head Angle Boundaries**:
   - Facial recognition (SFace) performs optimally when head yaw, pitch, and roll angles remain within $\pm 30^\circ$ of frontal orientation. Extreme profile views (over $45^\circ$) reduce Cosine Similarity match score.
3. **Occlusion & Face Masks**:
   - Heavy facial occlusions (full face masks, dark sunglasses covering eyes) obscure key landmark points used by SFace, preventing successful feature extraction.
4. **Single-Camera Input Stream**:
   - The AI recognition pipeline processes one camera/video feed at a time. Multi-camera concurrent processing requires running separate application instances.
5. **CPU Hardware Latency**:
   - Designed for low-spec CPU execution (Intel Core i3-12100). Real-time processing speed averages 25–30 FPS at $640 \times 480$ resolution. Processing high-resolution $4\text{K}$ video streams on low-end CPUs may increase per-frame latency.
6. **Mobile Camera Adapter Scope**:
   - The DroidCam mobile camera adapter is provided for **development testing purposes only**. Real-world deployment relies on standard USB webcams or integrated laptop cameras.
