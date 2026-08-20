# UI Walkthrough & Sitemap Documentation

## 1. Executive Summary & Design System

The AI-Enabled Smart Attendance System user interface is built with CustomTkinter using a standardized **dark-blue** color palette (`#1F497D` primary accent, `#2ECC71` success green, `#E74C3C` error red, `#F39C12` warning orange).

The application interface follows a **Unified Application Shell** design featuring:
- **Left Navigation Sidebar**: Quick tab access to all 5 primary view modules.
- **Topbar Status Bar**: System title, logged-in username, role badge (`[ADMIN]` / `[TEACHER]`), AI model status indicator (`AI Status: MODEL AVAILABLE`), and Logout button.
- **Central Dynamic Content Area**: Swaps view frames cleanly (`DashboardViewFrame`, `StudentManagementFrame`, `AttendanceViewFrame`, `ReportsViewFrame`, `AnalyticsViewFrame`).

---

## 2. Interface View Sitemap

```text
Application Root Window (MainWindow)
├── Topbar Header
│   ├── App Title ("AI-Enabled Smart Attendance System")
│   ├── User & Role Indicator ("Admin [ADMIN]")
│   ├── AI Engine Status Badge ("AI Status: MODEL AVAILABLE")
│   └── Logout Action Button
│
├── Left Sidebar Menu
│   ├── Dashboard Button
│   ├── Students Button
│   ├── AI Attendance Button
│   ├── Reports Button
│   └── Analytics Button
│
└── Central Content Area (View Switcher)
    ├── [View 1] DashboardViewFrame
    │   ├── 4 Summary Stat Cards (Total, Present, Absent, Attendance %)
    │   ├── Recent Attendance Activity Table
    │   └── Quick Action Navigation Buttons
    │
    ├── [View 2] StudentManagementFrame
    │   ├── Filter & Search Header
    │   ├── Student List Table (Code, Name, Class, Section, Status, Actions)
    │   ├── Add Student Modal Dialog
    │   ├── Edit Student Modal Dialog
    │   └── Face Registration Window (5-sample automated capture preview)
    │
    ├── [View 3] AttendanceViewFrame
    │   ├── Video Source Selector (Camera 0, Image, Video, Mobile)
    │   ├── Real-Time OpenCV Video Stream Canvas (YuNet Green Bounding Boxes)
    │   ├── Live Activity Feed Log
    │   └── Engine Control Buttons (Start / Stop Attendance)
    │
    ├── [View 4] ReportsViewFrame
    │   ├── Multi-Criteria Filter Bar (Start Date, End Date, Query, Class, Status)
    │   ├── Filtered Attendance Records Table
    │   ├── Inline Manual Correction Dialog
    │   └── Export Buttons (Export CSV, Export Excel)
    │
    └── [View 5] AnalyticsViewFrame
        ├── Timeframe Selector (7 / 14 / 30 Days)
        ├── 2x2 Grid Matplotlib Visual Analytics Charts
        │   ├── Chart 1: Daily Attendance Trend (Line/Bar Chart)
        │   ├── Chart 2: Status Distribution (Donut Chart)
        │   ├── Chart 3: Monthly Attendance Rate (Line Chart)
        │   └── Chart 4: Student Performance Breakdown (Category Bar Chart)
        └── Manual Chart Refresh Button
```

---

## 3. Reusable UI Components

1. **`ConfirmationDialog` (`app/ui/components.py`)**: Modal confirmation dialog preventing accidental student deactivations, face removals, manual corrections, or session logouts.
2. **`EmptyStateWidget` (`app/ui/components.py`)**: Clean placeholder widget providing informative feedback when search results return zero matching records.
