# Attendance Reports & Data Export System Architecture

## 1. Executive Summary

The **Attendance Reports & Management System** provides comprehensive multi-criteria filtering, student attendance percentage analytics, authorized manual attendance record corrections, and file export to CSV and Excel (`.xlsx` via OpenPyXL).

---

## 2. Multi-Criteria Filtering Architecture

```text
[ Start Date / End Date ] + [ Student Search ] + [ Class Filter ] + [ Status Filter ]
                                          ↓
                      search_attendance_records() [RBAC Check]
                                          ↓
                             Parameterized SQLite Query
                                          ↓
                          Filtered Attendance Records
                                 /           \
                 CustomTkinter Table View   Export (CSV / OpenPyXL Excel)
```

- **Supported Statuses**: `Present`, `Absent`, `Late`, `Excused`.
- **Date Format**: `YYYY-MM-DD` (validated using `strptime`).
- **Combinable Filters**: All filters can be combined dynamically (e.g. Date Range + Class + Status).

---

## 3. Student Attendance Analytics Formulas

| Metric | Calculation & Rule |
| :--- | :--- |
| **Total Days** | Total recorded session days for student within selected date range. |
| **Present Count** | Count of records with `status = 'Present'`. |
| **Absent Count** | Count of records with `status = 'Absent'`. |
| **Late Count** | Count of records with `status = 'Late'`. |
| **Excused Count** | Count of records with `status = 'Excused'`. |
| **Attendance %** | $\begin{cases} \frac{\text{Present Count}}{\text{Total Days}} \times 100.0\% & \text{if Total Days} > 0 \\ 0.0\% & \text{otherwise} \end{cases}$ |

---

## 4. Manual Correction & Security Model

- **Authorized Overrides Only**: Backend service (`correct_attendance_record()`) verifies active session (`SessionManager`). Unauthenticated requests throw `PermissionError`.
- **Data Integrity**: Parameterized SQL `UPDATE attendance SET status = ?, attendance_time = ? WHERE id = ?`.
- **Zero Sensitive Data Exposure**: Exports write ONLY academic attendance metadata. ZERO raw face images, biometric embeddings, password hashes, or secrets are exported.
