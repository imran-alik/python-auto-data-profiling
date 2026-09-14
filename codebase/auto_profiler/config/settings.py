"""Profiler configuration and path resolution."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


@dataclass
class ProfilerConfig:
    """Runtime configuration for profiling runs."""

    source_csv: Path = field(default_factory=lambda: _repo_root() / "data" / "source" / "samples" / "telco_features_sample.csv")
    report_output_dir: Path = field(default_factory=lambda: _repo_root() / "visualizations")
    evidence_dir: Path = field(default_factory=lambda: _repo_root() / "data" / "evidence")
    medallion_dir: Path = field(default_factory=lambda: _repo_root() / "medallion" / "output")
    quantile_bins: int = 5
    correlation_threshold: float = 0.5
    min_rows: int = 10
    max_null_pct: float = 40.0
    run_name: str = "telco_sample"

    def ensure_dirs(self) -> None:
        self.report_output_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.medallion_dir.mkdir(parents=True, exist_ok=True)
