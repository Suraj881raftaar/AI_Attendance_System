# Visual Analytics System Architecture & Specifications

## 1. Executive Summary

The **Charts & Visual Analytics System** provides lightweight, CPU-first graphical chart rendering displaying real attendance data from the local SQLite database.

It renders 4 visual analytics panels using Matplotlib embedded in CustomTkinter via `FigureCanvasTkAgg`.

---

## 2. Analytics Metrics & Boundary Rules

| Chart Panel | Data Source & Formula | Rendering Representation |
| :--- | :--- | :--- |
| **Daily Attendance Trend** | Aggregates daily Present (and Late) vs Absent count over past N days (7, 14, 30 days). | Dual-Line plot / Grouped Bar chart. |
| **Status Distribution** | Proportional count breakdown (`Present`, `Absent`, `Late`, `Excused`) for selected date. | Donut / Pie chart with percentage values. |
| **Monthly Trend** | Monthly average attendance rate ($\frac{\text{Present Count}}{\text{Total Records}} \times 100.0\%$) over past M months. | Column Bar chart with rate labels. |
| **Student Performance** | Categorizes active registered students into 3 attendance rate bands: <br>• **Excellent**: $> 90.0\%$ <br>• **Good**: $75.0\% \le \text{Rate} \le 90.0\%$ <br>• **At-Risk**: $< 75.0\%$ | Category Bar chart with student counts. |

---

## 3. Memory & Figure Management

- **Clean Redraws**: When refreshing charts or changing timeframes, the view invokes `cleanup_figure_canvas(canvas, figure)` which calls `canvas.get_tk_widget().destroy()`, `fig.clear()`, and `plt.close(fig)`.
- **Zero Leak Guarantee**: Prevents accumulation of orphaned Matplotlib figures and Tkinter widget handles.

---

## 4. Security & Data Safety

- **Local CPU-First Processing**: 100% offline local Matplotlib rendering.
- **Zero Sensitive Data Exposure**: Visualizations display aggregated statistics. ZERO raw face images, 128D embeddings, password hashes, or secrets are rendered or logged.
