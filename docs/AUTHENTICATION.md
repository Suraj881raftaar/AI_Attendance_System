# Authentication & User Management Specification

## 1. Overview

The **AI-Enabled Smart Attendance System** includes a secure, lightweight, and local authentication subsystem (`app/auth/`). It provides role-based access control (RBAC), cryptographic password security, in-memory session management, login brute-force protection, and first-run administrator onboarding.

---

## 2. Password Security Architecture

- **Algorithm**: PBKDF2-HMAC-SHA256 (NIST recommended key derivation).
- **Iteration Count**: 100,000 rounds.
- **Salt Generation**: 16 bytes (128 bits) of cryptographically random salt generated using Python's `secrets` module.
- **Hash String Format**: `pbkdf2:sha256:100000$<salt_hex>$<hash_hex>`
- **Verification**: Timing-attack resistant hash comparison using `hmac.compare_digest`.
- **Zero Plaintext Storage**: Plaintext passwords are never persisted to disk, logged, or exposed in UI code.

---

## 3. User Roles & Authorization

The system enforces role-based authorization via application logic in `app/auth/session.py`:

| Role | Permissions |
| :--- | :--- |
| `admin` | Full system access: User management, system configuration, student management, attendance recording, reports, face data. |
| `teacher` | Standard staff access: View dashboard, take attendance, view student records, generate reports. |

> **Role Hierarchy**: An `admin` user implicitly inherits all `teacher` privileges.

---

## 4. Session Management

- **Implementation**: In-memory singleton `SessionManager` (`app/auth/session.py`).
- **Session State**: Tracks `user_id`, `username`, `role`, and active status.
- **Lifetime**: Session lives in memory for the application run. Calling `logout()` immediately clears all session state.
- **Security Boundary**: Role checks occur via backend functions (`session.has_role('admin')`) rather than relying solely on UI element visibility.

---

## 5. Brute-Force & Login Protection

- **Tracking**: `LoginProtector` (`app/auth/protection.py`) tracks failed authentication attempts per username.
- **Max Attempts**: 5 consecutive failed attempts allowed.
- **Lockout Duration**: 30-second temporary lockout triggered upon reaching 5 failures.
- **Reset**: Successful authentication resets the failure counter to 0.

---

## 6. First-Run Setup Mechanism

- **Condition**: Detected when `count_users() == 0`.
- **Flow**: `setup_first_admin(username, password)` validates credentials, hashes the password, creates the primary administrator account, and initializes the session.
- **Security**: No default passwords or hardcoded admin accounts exist in source code. Once an initial user exists, subsequent first-run setup calls are rejected.

---

## 7. Password Modification

- **Function**: `change_password(user_id, old_password, new_password)`
- **Validation**: Requires verifying the existing password before applying the update. Minimum new password length: 6 characters.
- **State Change**: Instantly invalidates the old hash and updates `password_hash` in `users`.
