"""Data types for recording per-job timing spans."""

from dataclasses import dataclass, field


@dataclass
class JobSpan:
    job_id: int
    label: str
    start: float
    end: float
    worker_id: int = 0


@dataclass
class StrategyResult:
    name: str
    color: str
    spans: list[JobSpan] = field(default_factory=list)

    @property
    def total(self) -> float:
        if not self.spans:
            return 0.0
        t0 = min(s.start for s in self.spans)
        return max(s.end for s in self.spans) - t0

    def normalised(self) -> list[JobSpan]:
        """Shift all spans so they start at t=0."""
        t0 = min(s.start for s in self.spans)
        return [
            JobSpan(s.job_id, s.label, s.start - t0, s.end - t0, s.worker_id)
            for s in self.spans
        ]
