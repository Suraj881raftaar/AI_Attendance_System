---
name: security-audit
description: Security and biometric data privacy auditing skill for AI Attendance System.
---

# Security Audit Skill

## Purpose
Audits local-first biometric data safety, authentication, RBAC authorization, password hashing, parameterized SQL, and secret protection.

## Checklist
1. **Biometric Privacy**: Verifies 128D feature vectors remain in local SQLite DB and raw camera frames are discarded in RAM.
2. **Authentication & RBAC**: Checks password hashing (`pbkdf2:sha256`), privilege checks (`ADMIN`/`TEACHER`), and RAM session destruction on logout.
3. **SQL Injection**: Ensures all database queries use parameterized placeholders (`?`).
4. **Secret Leaks**: Scans for passwords, API keys, tokens, or hardcoded personal paths.

## Rule
Never log or display raw password hashes or biometric feature vectors.
