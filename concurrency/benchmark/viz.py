"""Speedup bar chart for benchmark results."""

from __future__ import annotations

from .types import BenchResult

try:
    import matplotlib.pyplot as plt

    HAS_PLOT = True
except ImportError:
    HAS_PLOT = False


def _plot_speedup(
    groups: list[list[BenchResult]],
    titles: list[str],
    save_path: str,
) -> None:
    if not HAS_PLOT:
        print("  matplotlib not installed — skipping chart.")
        return

    palette = {
        "seq": "#E74C3C",
        "thr": "#3498DB",
        "async": "#2ECC71",
        "proc": "#9B59B6",
    }

    fig, axes = plt.subplots(1, len(groups), figsize=(6 * len(groups), 5))
    if len(groups) == 1:
        axes = [axes]
    fig.suptitle(
        "Python Concurrency — Speedup over sequential baseline",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )
    fig.patch.set_facecolor("white")

    color_order = [palette["seq"], palette["thr"], palette["async"], palette["proc"]]

    for ax, results, title in zip(axes, groups, titles):
        ax.set_facecolor("#F8F9FA")
        baseline = results[0].seconds
        labels = [r.label.split("(")[0].strip() for r in results]
        speedups = [baseline / r.seconds for r in results]
        colors = color_order[: len(results)]

        bars = ax.barh(
            labels, speedups, color=colors, edgecolor="white", linewidth=0.8, alpha=0.9
        )
        ax.axvline(1.0, color="#E74C3C", linestyle="--", linewidth=1.2, alpha=0.7)
        ax.set_xlabel("Speedup (×)", fontsize=10)
        ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
        ax.set_xlim(0, max(speedups) * 1.3)
        for bar, sp in zip(bars, speedups):
            ax.text(
                bar.get_width() + 0.03,
                bar.get_y() + bar.get_height() / 2,
                f"{sp:.1f}×",
                va="center",
                fontsize=9,
                fontweight="bold",
            )
        ax.invert_yaxis()

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"\n  Chart saved → {save_path}\n")
