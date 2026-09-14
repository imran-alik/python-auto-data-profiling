"""Tests for quantile binning and SQL export."""

import pandas as pd

from auto_profiler.export.sql_case_generator import generate_case_sql
from auto_profiler.features.binning import quantile_bins


def test_quantile_bins_supported():
    series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], name="score")
    spec = quantile_bins(series, n_bins=4)
    assert spec["supported"] is True
    assert "stability_hash" in spec
    assert len(spec["edges"]) >= 2


def test_stability_hash_deterministic():
    series = pd.Series(list(range(100)), name="v")
    a = quantile_bins(series, n_bins=5)
    b = quantile_bins(series, n_bins=5)
    assert a["stability_hash"] == b["stability_hash"]


def test_generate_case_sql():
    spec = {
        "column": "tenure",
        "supported": True,
        "edges": [0.0, 10.0, 20.0],
        "labels": ["Q1", "Q2"],
    }
    sql = generate_case_sql(spec)
    assert "CASE" in sql
    assert "tenure" in sql
    assert "Q1" in sql
