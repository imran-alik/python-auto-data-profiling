"""Tests for HTML report generation."""

from pathlib import Path

import pandas as pd

from auto_profiler.profiling.stats_engine import build_profile_stats
from auto_profiler.visualizations.html_report import render_html_report


def test_render_html_report_creates_file(tmp_path: Path):
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4.0, 5.0, 6.0]})
    stats = build_profile_stats(df)
    out = tmp_path / "report.html"
    render_html_report(
        df,
        stats,
        health={"score": 95.0, "columns_scored": 2},
        alerts=[],
        bin_specs=[],
        output_path=out,
        run_name="test",
    )
    content = out.read_text(encoding="utf-8")
    assert "Python Auto Data Profiling" in content
    assert "plotly" in content.lower()
