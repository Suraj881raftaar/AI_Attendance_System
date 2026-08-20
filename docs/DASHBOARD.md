# Management Dashboard System Architecture & Specifications

## 1. Executive Summary

The **Management Dashboard** serves as the primary landing view for administrators and teachers after successful authentication in the AI-Enabled Smart Attendance System.

It aggregates live metrics from the local SQLite database (`students` and `attendance` tables) and provides quick navigation actions to start attendance recognition, register new students, or manually refresh data.

---

## 2. Summary Metrics Definitions & Calculations

| Metric | Card Label | Calculation Formula & Rules |
| :--- | :--- | :--- |
| **Total Students** | `TOTAL STUDENTS` | Count of active registered students (`status = 'active'`). Inactive students excluded. |
| **Present Today** | `PRESENT TODAY` | Unique active students marked Present for today's local date (`YYYY-MM-DD`). |
| **Absent Today** | `ABSENT TODAY` | $\max(0, \text{Total Active} - \text{Present Today})$. Never negative. |
| **Attendance %** | `ATTENDANCE %` | $\begin{cases} \frac{\text{Present Today}}{\text{Total Active}} \times 100.0\% & \text{if Total Active} > 0 \\ 0.0\% & \text{otherwise} \end{cases}$ |

---

## 3. UI Layout & Navigation Integration

```text
+----------------------------------------------------------------------------+
|  Management Dashboard                           AI Engine: MODEL AVAILABLE |
+----------------------------------------------------------------------------+
| [ TOTAL STUDENTS ] [ PRESENT TODAY ] [ ABSENT TODAY ] [ ATTENDANCE % ]     |
| [       45       ] [      38       ] [       7      ] [    84.44%    ]     |
+----------------------------------------------------+-----------------------+
| Recent Attendance Activity                         | Quick Actions         |
| -------------------------------------------------- | --------------------- |
| Student Name  | Student ID | Class | Time  | Status| [Start Camera (Green)]|
| Jane Smith    | STU-102    | 12-A  | 09:15 |Present| [Add Student (Blue)]  |
| Alice Active  | STU-502    | 12-B  | 09:12 |Present| [Refresh (Gray)]      |
+----------------------------------------------------+-----------------------+
```

---

## 4. Auto-Refresh & Security Model

- **Safe Auto-Refresh**: Background timer callback runs every 10 seconds while the dashboard view is active. Destructor cleanly cancels timer callbacks (`after_cancel`) to prevent orphaned timer memory leaks.
- **Backend RBAC Authorization**: Service layer (`get_dashboard_metrics()`) verifies active user session (`SessionManager`). Unauthenticated requests throw `PermissionError`.
- **Zero Sensitive Exposure**: Does NOT expose raw biometric embeddings, face photos, or user password hashes.
