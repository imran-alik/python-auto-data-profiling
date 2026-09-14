"""Tests for reusable profiler_core package."""


import pandas as pd

from profiler_core import (
    build_alerts,
    compute_health_score,
    evaluate_guardrails,
    run_failure_checks,
)


def test_failure_checks_empty_frame():
    result = run_failure_checks(pd.DataFrame())
    assert result["passed"] is False
    assert "empty_dataframe" in result["issues"]


def test_health_score_range():
    columns = [{"name": "a", "null_pct": 5.0, "cardinality": 10, "row_count": 100, "dtype": "int64"}]
    health = compute_health_score(columns)
    assert 0 <= health["score"] <= 100


def test_guardrails_violation_on_high_nulls():
    stats = {
        "row_count": 100,
        "columns": [{"name": "x", "null_pct": 55.0}],
    }
    result = evaluate_guardrails(stats, max_null_pct=40.0)
    assert result["passed"] is False


def test_build_alerts_warn_level():
    columns = [{"name": "x", "null_pct": 25.0, "cardinality": 5, "row_count": 100, "dtype": "object"}]
    alerts = build_alerts(columns, null_warn_pct=20.0)
    assert any(a["level"] == "warn" for a in alerts)
