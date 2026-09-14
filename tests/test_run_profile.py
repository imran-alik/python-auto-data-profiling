"""Integration test for full profiling run."""

from pathlib import Path

import pandas as pd

from auto_profiler.config.settings import ProfilerConfig
from auto_profiler.orchestration.run_profile import run_profile


def test_run_profile_end_to_end(tmp_path: Path):
    csv = tmp_path / "mini.csv"
    pd.DataFrame(
        {
            "id": list(range(1, 16)),
            "value": [float(i * 2) for i in range(1, 16)],
            "category": ["a", "b", "c"] * 5,
        }
    ).to_csv(csv, index=False)

    config = ProfilerConfig(
        source_csv=csv,
        report_output_dir=tmp_path / "reports",
        evidence_dir=tmp_path / "evidence",
        medallion_dir=tmp_path / "medallion",
        run_name="integration_test",
    )
    summary = run_profile(config)

    assert summary["row_count"] == 15
    assert summary["guardrails"]["passed"] is True
    report_rel = summary["report_path"]
    report_file = tmp_path / "reports" / Path(str(report_rel)).name
    assert report_file.exists()
    assert "health_score" in summary
