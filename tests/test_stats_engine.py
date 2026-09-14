"""Tests for profiling stats engine."""

import pandas as pd

from auto_profiler.profiling.stats_engine import build_profile_stats, compute_correlations


def test_build_profile_stats_counts():
    df = pd.DataFrame({"a": [1, 2, None], "b": ["x", "y", "z"]})
    stats = build_profile_stats(df)
    assert stats["row_count"] == 3
    assert stats["column_count"] == 2
    assert len(stats["columns"]) == 2


def test_null_pct_computed():
    df = pd.DataFrame({"a": [1, None, None]})
    stats = build_profile_stats(df)
    col_a = stats["columns"][0]
    assert col_a["null_count"] == 2
    assert col_a["null_pct"] == 66.67


def test_correlations_detected():
    df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 6, 8, 10]})
    pairs = compute_correlations(df, threshold=0.9)
    assert len(pairs) == 1
    assert pairs[0]["column_a"] in ("x", "y")
