"""Aggregate health score from column-level stats."""

from __future__ import annotations


def compute_health_score(column_stats: list[dict[str, object]]) -> dict[str, float | int]:
    """Score 0-100 from null rate and cardinality signals."""
    if not column_stats:
        return {"score": 0.0, "columns_scored": 0}

    penalties: list[float] = []
    for col in column_stats:
        null_pct = float(col.get("null_pct", 0.0))
        cardinality = int(col.get("cardinality", 0))
        row_count = int(col.get("row_count", 1)) or 1
        unique_ratio = cardinality / row_count

        penalty = min(null_pct, 50.0)
        if unique_ratio >= 0.99 and col.get("dtype") not in ("int64", "float64", "Int64", "Float64"):
            penalty += 10.0
        penalties.append(penalty)

    avg_penalty = sum(penalties) / len(penalties)
    score = max(0.0, round(100.0 - avg_penalty, 2))
    return {"score": score, "columns_scored": len(column_stats)}
