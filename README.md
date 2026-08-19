# AI-Enabled Smart Attendance System

**Project Type:** Class 12 Academic Project  
**Application Type:** Desktop Application  
**Primary Goal:** Build a genuinely AI-powered attendance system using local face recognition.

---

## 📌 Features Overview

- **Secure Authentication:** Password-protected teacher/admin access with salted hashing.
- **Student Management:** Full CRUD operations (Add, Edit, Delete, Search) with duplicate roll number prevention.
- **AI Face Registration & Recognition:** Real-time facial sample collection, feature extraction, and offline embedding matching.
- **Automatic Attendance Engine:** Real-time webcam identification, automated record creation, and duplicate attendance prevention.
- **Dashboard & Analytics:** Real-time attendance percentage, statistics, and graphical visual charts.
- **Reports & Exporting:** Searchable history with Excel and CSV export functionality.
- **Privacy & Offline First:** All biometric data and database records remain strictly local on the host system.

---

## 📁 Repository Structure

```text
AI_Attendance_System/
│
├── app/
│   ├── main.py            # Application entry point
│   ├── config.py          # Global path & app configuration
│   ├── database.py        # SQLite connection & CRUD operations
│   ├── security.py        # Password hashing & authentication helpers
│   │
│   ├── auth/              # Teacher / admin authentication
│   ├── students/          # Student management logic
│   ├── attendance/        # Attendance engine logic
│   ├── ai/                # AI face detector & recognizer models
│   ├── reports/           # Analytics, exporters, and charts
│   └── ui/                # CustomTkinter GUI views & components
│
├── data/
│   ├── attendance.db      # SQLite database
│   └── face_data/         # Local student face embeddings
│
├── assets/                # Application branding & UI icons
├── tests/                 # Unit & integration tests
├── docs/                  # Project documentation & viva guide
├── requirements.txt       # Dependencies
└── README.md
```

---

## 🚀 Setup & Execution

### 1. Requirements

- Python 3.10+ (Tested on Python 3.13)
- Windows OS (Desktop Application)
- Webcam (For face registration & attendance taking)

### 2. Environment Setup

```bash
# Create virtual environment
py -m venv venv

# Activate virtual environment (PowerShell)
.\venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt
```

### 3. Running the Application

```bash
python main.py
```

---

## 📊 Staged Implementation Plan Status

- [x] **STAGE 0 — Project Initialization** (Foundation & Architecture set up)
- [ ] **STAGE 1 — Database & Core Foundation**
- [ ] **STAGE 2 — Authentication**
- [ ] **STAGE 3 — Student Management UI**
- [ ] **STAGE 4 — AI Model Integration**
- [ ] **STAGE 5 — Face Registration**
- [ ] **STAGE 6 — AI Attendance Engine**
- [ ] **STAGE 7 — Dashboard**
- [ ] **STAGE 8 — Attendance Management & Reports**
- [ ] **STAGE 9 — Charts & Analytics**
- [ ] **STAGE 10 — UI/UX Polish**
- [ ] **STAGE 11 — Testing & Hardening**
- [ ] **STAGE 12 — Packaging**
- [ ] **STAGE 13 — Documentation**
- [ ] **STAGE 14 — Viva Preparation**
