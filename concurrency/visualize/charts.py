"""Publication-ready chart functions (figures 1–5)."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # non-interactive backend — no display required
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from .config import C
from .types import StrategyResult

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linestyle": "--",
        "figure.dpi": 140,
    }
)


# =============================================================================
# Shared chart helpers
# =============================================================================


def _gantt_panel(ax: plt.Axes, strat: StrategyResult, title: str, x_max: float) -> None:
    """One Gantt panel — one strategy. Overlapping bars = true parallelism."""
    ax.set_facecolor(C["bg"])
    ax.set_title(
        title, fontsize=10, fontweight="bold", pad=6, color=strat.color, loc="left"
    )
    ax.set_xlabel("Time (seconds)", fontsize=9)

    spans = strat.normalised()
    n_jobs = len(spans)
    height = 0.55

    for span in sorted(spans, key=lambda s: s.job_id):
        y = n_jobs - 1 - span.job_id
        dur = span.end - span.start
        ax.barh(
            y,
            dur,
            left=span.start,
            height=height,
            color=strat.color,
            alpha=0.82,
            edgecolor="white",
            linewidth=0.7,
        )
        ax.text(
            span.start + dur / 2,
            y,
            f"{dur*1000:.0f}ms",
            ha="center",
            va="center",
            fontsize=7,
            color="white",
            fontweight="bold",
        )

    ax.set_yticks(range(n_jobs))
    ax.set_yticklabels([f"Job {i}" for i in range(n_jobs - 1, -1, -1)], fontsize=8)
    ax.set_xlim(0, x_max * 1.12)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.2fs"))

    total = strat.total
    ax.axvline(total, color=strat.color, linestyle=":", linewidth=1.4, alpha=0.7)
    ax.text(
        total + x_max * 0.01,
        n_jobs - 0.6,
        f"total\n{total:.2f}s",
        ha="left",
        va="top",
        fontsize=8,
        color=strat.color,
        fontweight="bold",
    )


def _bar_speedup(ax: plt.Axes, strategies: list[StrategyResult], title: str) -> None:
    """Horizontal speedup bar chart relative to the sequential baseline."""
    baseline = strategies[0].total
    labels = [s.name.replace("\n", " ") for s in strategies]
    speedups = [baseline / s.total for s in strategies]
    colors = [s.color for s in strategies]

    ax.set_facecolor(C["bg"])
    ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
    ax.set_xlabel("Speedup over sequential (×)", fontsize=9)

    bars = ax.barh(
        labels,
        speedups,
        color=colors,
        edgecolor="white",
        linewidth=0.8,
        height=0.55,
        alpha=0.9,
    )
    ax.axvline(
        1.0,
        color=C["seq"],
        linestyle="--",
        linewidth=1.4,
        alpha=0.7,
        label="Baseline (1×)",
    )

    for bar, sp in zip(bars, speedups):
        ax.text(
            bar.get_width() + 0.04,
            bar.get_y() + bar.get_height() / 2,
            f"{sp:.1f}×",
            va="center",
            fontsize=9,
            fontweight="bold",
        )

    ax.set_xlim(0, max(speedups) * 1.3)
    ax.invert_yaxis()
    ax.legend(fontsize=8)


# =============================================================================
# Figure 1 — I/O Gantt: Support Ticket Triage
# =============================================================================


def figure1_io_gantt(strategies: list[StrategyResult], save: bool) -> None:
    n = len(strategies)
    fig, axes = plt.subplots(
        1, n + 1, figsize=(20, 5), gridspec_kw={"width_ratios": [1] * n + [0.75]}
    )
    fig.suptitle(
        "Support Ticket Triage — 6 LLM Calls (phi3.5:3.8b)",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )
    fig.patch.set_facecolor("white")

    x_max = max(s.total for s in strategies)
    titles = ["Sequential", "Threading  (6 workers)", "AsyncIO  (gather)"]
    for ax, strat, title in zip(axes[:-1], strategies, titles):
        _gantt_panel(ax, strat, title, x_max)
    _bar_speedup(axes[-1], strategies, "Speedup")

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    if save:
        fig.savefig("concurrency/fig1_io_gantt.png", bbox_inches="tight", dpi=150)
        print("  Saved → concurrency/fig1_io_gantt.png")
    else:
        plt.show()


# =============================================================================
# Figure 2 — CPU Gantt: Local Inference (GIL trap)
# =============================================================================


def figure2_cpu_gantt(strategies: list[StrategyResult], save: bool) -> None:
    n = len(strategies)
    fig, axes = plt.subplots(
        1, n + 1, figsize=(20, 5), gridspec_kw={"width_ratios": [1] * n + [0.75]}
    )
    fig.suptitle(
        "Local Inference — 6 CPU Batches  (GIL trap revealed)",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )
    fig.patch.set_facecolor("white")

    x_max = max(s.total for s in strategies)
    titles = [
        "Sequential",
        "Threading  (GIL blocks)",
        "Multiprocessing  (true parallel)",
    ]
    for ax, strat, title in zip(axes[:-1], strategies, titles):
        _gantt_panel(ax, strat, title, x_max)
    _bar_speedup(axes[-1], strategies, "Speedup")

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    if save:
        fig.savefig("concurrency/fig2_cpu_gantt.png", bbox_inches="tight", dpi=150)
        print("  Saved → concurrency/fig2_cpu_gantt.png")
    else:
        plt.show()


# =============================================================================
# Figure 3 — Embedding Gantt: Knowledge Base
# =============================================================================


def figure3_embed_gantt(strategies: list[StrategyResult], save: bool) -> None:
    n = len(strategies)
    fig, axes = plt.subplots(
        1, n + 1, figsize=(14, 5), gridspec_kw={"width_ratios": [1] * n + [0.75]}
    )
    fig.suptitle(
        "Knowledge Base Embedding — 8 Chunks  (nomic-embed-text)",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )
    fig.patch.set_facecolor("white")

    x_max = max(s.total for s in strategies)
    titles = ["Sequential", "AsyncIO  (gather)"]
    for ax, strat, title in zip(axes[:-1], strategies, titles):
        _gantt_panel(ax, strat, title, x_max)
    _bar_speedup(axes[-1], strategies, "Speedup")

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    if save:
        fig.savefig("concurrency/fig3_embed_gantt.png", bbox_inches="tight", dpi=150)
        print("  Saved → concurrency/fig3_embed_gantt.png")
    else:
        plt.show()


# =============================================================================
# Figure 4 — RAG Pipeline Waterfall
# =============================================================================


def figure4_rag_waterfall(
    embed_ms: float, retrieve_ms: float, generate_ms: float, save: bool
) -> None:
    fig, ax = plt.subplots(figsize=(11, 4))
    fig.suptitle(
        "RAG Pipeline — Step-by-Step Latency Breakdown",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )
    fig.patch.set_facecolor("white")
    ax.set_facecolor(C["bg"])

    steps = ["1. Embed query", "2. Cosine retrieval", "3. Generate answer"]
    labels = ["nomic-embed-text", "in-process (no API)", "phi3.5:3.8b"]
    times = [embed_ms, retrieve_ms, generate_ms]
    colors = [C["async"], "#F39C12", C["proc"]]
    starts = [0.0, embed_ms, embed_ms + retrieve_ms]

    for i, (step, lbl, t, color, start) in enumerate(
        zip(steps, labels, times, colors, starts)
    ):
        ax.barh(
            i,
            t,
            left=start,
            height=0.5,
            color=color,
            alpha=0.88,
            edgecolor="white",
            linewidth=0.8,
        )
        dur_str = f"{t:.0f} ms" if t >= 5 else f"{t:.1f} ms"
        ax.text(
            start + t / 2,
            i,
            dur_str,
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold",
            color="white" if t > 30 else C["text"],
        )
        ax.text(
            -sum(times) * 0.01,
            i,
            f"{step}  ({lbl})",
            ha="right",
            va="center",
            fontsize=9,
            color=C["text"],
        )

    total = sum(times)
    ax.set_yticks([])
    ax.set_xlabel("Time (ms)", fontsize=10)
    ax.invert_yaxis()
    ax.set_xlim(-total * 0.42, total * 1.12)
    ax.text(
        total * 1.01,
        2.25,
        f"Total:  {total:.0f} ms",
        ha="left",
        va="center",
        fontsize=10,
        fontweight="bold",
        color=C["text"],
    )
    ax.axvline(0, color="#888", linewidth=0.8)

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    if save:
        fig.savefig("concurrency/fig4_rag_waterfall.png", bbox_inches="tight", dpi=150)
        print("  Saved → concurrency/fig4_rag_waterfall.png")
    else:
        plt.show()


# =============================================================================
# Figure 5 — Grand Summary: All Strategies, All Use-Cases
# =============================================================================


def figure5_summary(
    io_strats: list[StrategyResult],
    cpu_strats: list[StrategyResult],
    embed_strats: list[StrategyResult],
    save: bool,
) -> None:
    fig = plt.figure(figsize=(17, 6))
    fig.suptitle(
        "Benchmark Summary — Sequential vs Threading vs AsyncIO vs Multiprocessing",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )
    fig.patch.set_facecolor("white")
    gs = gridspec.GridSpec(1, 3, figure=fig, wspace=0.42)

    def _panel(ax: plt.Axes, strats: list[StrategyResult], title: str) -> None:
        ax.set_facecolor(C["bg"])
        ax.set_title(title, fontsize=10, fontweight="bold", pad=8)
        baseline = strats[0].total
        labels = [s.name.replace("\n", " ") for s in strats]
        times = [s.total for s in strats]
        colors = [s.color for s in strats]

        x = np.arange(len(strats))
        bars = ax.bar(
            x,
            times,
            color=colors,
            edgecolor="white",
            linewidth=0.8,
            width=0.55,
            alpha=0.9,
        )

        for bar, t, sp in zip(bars, times, [baseline / t for t in times]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(times) * 0.02,
                f"{sp:.1f}x\n{t:.2f}s",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
                linespacing=1.4,
            )

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8.5, rotation=15, ha="right")
        ax.set_ylabel("Total time (s)", fontsize=9)
        ax.set_ylim(0, max(times) * 1.45)
        ax.tick_params(axis="x", pad=4)

    _panel(fig.add_subplot(gs[0]), io_strats, "I/O-Bound — Ticket Triage")
    _panel(fig.add_subplot(gs[1]), cpu_strats, "CPU-Bound — Local Inference")
    _panel(fig.add_subplot(gs[2]), embed_strats, "I/O-Bound — KB Embedding")

    legend_patches = [
        mpatches.Patch(color=C["seq"], label="Sequential"),
        mpatches.Patch(color=C["thread"], label="Threading"),
        mpatches.Patch(color=C["async"], label="AsyncIO"),
        mpatches.Patch(color=C["proc"], label="Multiprocessing"),
    ]
    fig.legend(
        handles=legend_patches,
        loc="lower center",
        ncol=4,
        fontsize=9,
        frameon=False,
        bbox_to_anchor=(0.5, 0.03),
    )

    fig.subplots_adjust(bottom=0.22, top=0.88, wspace=0.40, left=0.07, right=0.98)
    if save:
        fig.savefig("concurrency/fig5_summary.png", bbox_inches="tight", dpi=150)
        print("  Saved → concurrency/fig5_summary.png")
    else:
        plt.show()
