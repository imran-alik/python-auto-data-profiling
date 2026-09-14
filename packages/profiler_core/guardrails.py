"""Configurable guardrails for profiling quality gates."""

from __future__ import annotations


def evaluate_guardrails(
    stats: dict[str, object],
    *,
    max_null_pct: float = 40.0,
    min_rows: int = 10,
) -> dict[str, object]:
    """Evaluate portfolio guardrails against profile stats."""
    row_count = int(stats.get("row_count", 0))
    columns = stats.get("columns", [])
    if not isinstance(columns, list):
        columns = []

    violations: list[str] = []
    if row_count < min_rows:
        violations.append(f"row_count_below_min:{row_count}<{min_rows}")

    for col in columns:
        if not isinstance(col, dict):
            continue
        null_pct = float(col.get("null_pct", 0.0))
        if null_pct > max_null_pct:
            violations.append(f"high_nulls:{col.get('name')}:{null_pct}")

    return {
        "passed": len(violations) == 0,
        "violations": violations,
        "thresholds": {"max_null_pct": max_null_pct, "min_rows": min_rows},
    }
