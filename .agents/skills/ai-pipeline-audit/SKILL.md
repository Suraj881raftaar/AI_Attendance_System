---
name: ai-pipeline-audit
description: YuNet face detection, SFace recognition, embedding, and 0.363 threshold auditing skill for AI Attendance System.
---

# AI Pipeline Audit Skill

## Purpose
Audits YuNet face detection, SFace 128D feature extraction, $L_2$ normalization, Cosine similarity matching, threshold $0.363$, 10-second safety cooldown, and unknown face rejection.

## Rules
- Implementation details must match academic documentation.
- Do NOT change the $0.363$ threshold.
- Do NOT modify ONNX model binaries.
