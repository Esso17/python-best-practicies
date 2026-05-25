"""Shared result type and print helpers."""

from dataclasses import dataclass, field

W = 76


@dataclass
class BenchResult:
    label: str
    seconds: float
    n_tasks: int = 0
    speedup: float = 1.0
    outputs: list = field(default_factory=list)

    @property
    def throughput(self) -> float:
        return self.n_tasks / self.seconds if self.seconds > 0 else 0.0


def _header(title: str) -> None:
    print(f"\n{'═' * W}\n  {title}\n{'═' * W}")


def _sub(s: str) -> None:
    print(f"\n  ── {s}")


def _table_header() -> None:
    print(f"\n  {'Strategy':<32} {'Time':>7}  {'Speedup':>8}   Bar")
    print("  " + "─" * 60)


def _row(label: str, secs: float, baseline: float) -> float:
    sp = baseline / secs if secs > 0 else 1.0
    bar = "█" * min(int(sp * 4), 28)
    print(f"  {label:<32} {secs:>6.2f}s  {sp:>7.1f}×   {bar}")
    return sp


def _summary_row(label: str, results: list[BenchResult]) -> None:
    seq = results[0].seconds
    best = min(results, key=lambda r: r.seconds)
    sp = seq / best.seconds
    print(
        f"  {label:<38} {seq:>8.2f}s  {best.seconds:>8.2f}s  {sp:>6.1f}×  {best.label}"
    )
