# UI/UX Design & Application Shell Architecture

## 1. Executive Summary

Stage 10 introduces a unified main application window container (`MainWindow`) hosting all views in a modern sidebar/topbar navigation shell for the AI-Enabled Smart Attendance System.

The interface is built using CustomTkinter with the standardized `dark-blue` theme mode, consistent typography hierarchy, reusable modal confirmation dialogs, and clear form validation feedback.

---

## 2. Layout Structure & Navigation Shell

```text
+----------------------------------------------------------------------------+
| AI-Enabled Smart Attendance System       User: Admin [ADMIN]  AI: READY   |
+-------------------++-------------------------------------------------------+
| NAVIGATION        ||                                                       |
| ----------------- ||                                                       |
| [ Dashboard    ]  ||                                                       |
| [ Students     ]  ||                  ACTIVE CONTENT VIEW                  |
| [ AI Attendance]  ||          (Dashboard / Students / Attendance /         |
| [ Reports      ]  ||                Reports / Analytics)                   |
| [ Analytics    ]  ||                                                       |
|                   ||                                                       |
|                   ||                                                       |
+-------------------++-------------------------------------------------------+
```

---

## 3. Reusable UI Components

1. **`MainWindow` (`app/ui/main_window.py`)**: Unified desktop application container hosting sidebar, topbar status bar (logged-in user, role badge, AI engine status), and view switcher.
2. **`ConfirmationDialog` (`app/ui/components.py`)**: Reusable modal confirmation dialog for action safety (Deactivating students, deleting face embeddings, manual corrections, logout).
3. **`EmptyStateWidget` (`app/ui/components.py`)**: Informative empty-state placeholder widget for empty tables, search results, or record lists.

---

## 4. Visual Language & Status Colors

- **Success / Recognized**: Green (`#2ECC71`)
- **Warning / Pending / Unknown**: Orange (`#F39C12`)
- **Error / Rejected / Deactivated**: Red (`#E74C3C`)
- **Primary / Action Buttons**: Dark Blue (`#1F497D`)
