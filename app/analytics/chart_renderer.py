from __future__ import annotations

import logging
from typing import Dict, Any, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except Exception:
    HAS_MATPLOTLIB = False

logger = logging.getLogger(__name__)


def create_daily_trend_figure(trend_data: Dict[str, Any], figsize: Tuple[float, float] = (5.0, 3.0)) -> Tuple[Optional[Any], Optional[Any]]:
    """Create a Matplotlib figure for Daily Attendance Trend (Present vs Absent)."""
    if not HAS_MATPLOTLIB:
        return None, None
    fig = Figure(figsize=figsize, dpi=100)
    fig.patch.set_facecolor("#2B2B2B")

    ax = fig.add_subplot(111)
    ax.set_facecolor("#2B2B2B")

    dates = trend_data.get("dates", [])
    p_counts = trend_data.get("present_counts", [])
    a_counts = trend_data.get("absent_counts", [])

    # Format x-axis short dates
    short_dates = [d[5:] if len(d) >= 10 else d for d in dates]

    if short_dates:
        ax.plot(short_dates, p_counts, marker="o", color="#2ECC71", linewidth=2, label="Present")
        ax.plot(short_dates, a_counts, marker="s", color="#E74C3C", linewidth=2, label="Absent")
        ax.set_title(f"Daily Attendance Trend ({trend_data.get('days', 7)} Days)", color="white", fontsize=11, fontweight="bold")
        ax.set_xlabel("Date", color="gray", fontsize=9)
        ax.set_ylabel("Student Count", color="gray", fontsize=9)
        ax.tick_params(colors="white", labelsize=8)
        ax.legend(facecolor="#2B2B2B", edgecolor="gray", labelcolor="white", fontsize=8)
        ax.grid(True, linestyle="--", alpha=0.3, color="gray")
    else:
        ax.text(0.5, 0.5, "No attendance data available", color="gray", ha="center", va="center")

    fig.tight_layout()
    return fig, ax


def create_status_distribution_figure(dist_data: Dict[str, Any], figsize: Tuple[float, float] = (5.0, 3.0)) -> Tuple[Optional[Any], Optional[Any]]:
    """Create a Matplotlib figure for Status Proportions Distribution (Donut Chart)."""
    if not HAS_MATPLOTLIB:
        return None, None
    fig = Figure(figsize=figsize, dpi=100)
    fig.patch.set_facecolor("#2B2B2B")

    ax = fig.add_subplot(111)
    ax.set_facecolor("#2B2B2B")

    dist = dist_data.get("distribution", {})
    labels = []
    sizes = []
    colors = []

    color_map = {
        "Present": "#2ECC71",
        "Absent": "#E74C3C",
        "Late": "#F39C12",
        "Excused": "#3498DB",
    }

    for k, v in dist.items():
        if v > 0:
            labels.append(f"{k} ({v})")
            sizes.append(v)
            colors.append(color_map.get(k, "gray"))

    if sizes:
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=140,
            pctdistance=0.75,
            textprops={"color": "white", "fontsize": 8},
        )
        # Make center donut hole
        centre_circle = plt.Circle((0, 0), 0.50, fc="#2B2B2B")
        fig.gca().add_artist(centre_circle)
        ax.set_title(f"Status Distribution ({dist_data.get('date', 'Today')})", color="white", fontsize=11, fontweight="bold")
    else:
        ax.text(0.5, 0.5, "No attendance for selected date", color="gray", ha="center", va="center")

    fig.tight_layout()
    return fig, ax


def create_monthly_trend_figure(monthly_data: Dict[str, Any], figsize: Tuple[float, float] = (5.0, 3.0)) -> Tuple[Optional[Any], Optional[Any]]:
    """Create a Matplotlib figure for Monthly Attendance Trend (% Rate)."""
    if not HAS_MATPLOTLIB:
        return None, None
    fig = Figure(figsize=figsize, dpi=100)
    fig.patch.set_facecolor("#2B2B2B")

    ax = fig.add_subplot(111)
    ax.set_facecolor("#2B2B2B")

    months = monthly_data.get("months", [])
    percentages = monthly_data.get("percentages", [])

    if months:
        bars = ax.bar(months, percentages, color="#3498DB", width=0.5)
        ax.set_ylim(0, 105)
        ax.set_title("Monthly Attendance Rate (%)", color="white", fontsize=11, fontweight="bold")
        ax.set_ylabel("Attendance %", color="gray", fontsize=9)
        ax.tick_params(colors="white", labelsize=8)
        ax.grid(axis="y", linestyle="--", alpha=0.3, color="gray")

        # Value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(
                    f"{height}%",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    color="white",
                    fontsize=8,
                )
    else:
        ax.text(0.5, 0.5, "No monthly attendance data available", color="gray", ha="center", va="center")

    fig.tight_layout()
    return fig, ax


def create_student_performance_figure(perf_data: Dict[str, Any], figsize: Tuple[float, float] = (5.0, 3.0)) -> Tuple[Optional[Any], Optional[Any]]:
    """Create a Matplotlib figure for Student Performance Categories (Bar Chart)."""
    if not HAS_MATPLOTLIB:
        return None, None
    fig = Figure(figsize=figsize, dpi=100)
    fig.patch.set_facecolor("#2B2B2B")

    ax = fig.add_subplot(111)
    ax.set_facecolor("#2B2B2B")

    cats = perf_data.get("categories", {})
    categories = list(cats.keys())
    counts = list(cats.values())
    bar_colors = ["#2ECC71", "#F39C12", "#E74C3C"]

    if any(c > 0 for c in counts):
        bars = ax.bar(categories, counts, color=bar_colors, width=0.5)
        ax.set_title("Student Performance Breakdown", color="white", fontsize=11, fontweight="bold")
        ax.set_ylabel("Student Count", color="gray", fontsize=9)
        ax.tick_params(colors="white", labelsize=8)
        ax.grid(axis="y", linestyle="--", alpha=0.3, color="gray")

        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(
                    f"{int(height)}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    color="white",
                    fontsize=9,
                    fontweight="bold",
                )
    else:
        ax.text(0.5, 0.5, "No student performance data available", color="gray", ha="center", va="center")

    fig.tight_layout()
    return fig, ax


def embed_figure_in_tkinter(parent_widget: Any, fig: Any) -> Optional[Any]:
    """Embed a Matplotlib figure inside a Tkinter/CustomTkinter parent widget cleanly."""
    if not HAS_MATPLOTLIB or fig is None:
        return None
    canvas = FigureCanvasTkAgg(fig, master=parent_widget)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    return canvas


def cleanup_figure_canvas(canvas: Optional[Any], fig: Optional[Any]) -> None:
    """Cleanly destroy Tkinter canvas widget and close Matplotlib figure to prevent memory leaks."""
    if not HAS_MATPLOTLIB:
        return

    if canvas is not None:
        try:
            canvas.get_tk_widget().destroy()
        except Exception as e:
            logger.debug(f"Error destroying canvas widget: {e}")

    if fig is not None:
        try:
            fig.clear()
            plt.close(fig)
        except Exception as e:
            logger.debug(f"Error closing figure: {e}")
