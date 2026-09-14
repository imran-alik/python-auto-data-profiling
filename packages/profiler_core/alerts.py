"""Alert builder for profiling anomalies."""

from __future__ import annotations

from enum import StrEnum


class AlertLevel(StrEnum):
    INFO = "info"
    WARN = "warn"
    CRITICAL = "critical"


def build_alerts(
    column_stats: list[dict[str, object]],
    *,
    null_warn_pct: float = 20.0,
    null_critical_pct: float = 50.0,
) -> list[dict[str, str]]:
    """Build human-readable alerts from column stats."""
    alerts: list[dict[str, str]] = []
    for col in column_stats:
        name = str(col.get("name", "unknown"))
        null_pct = float(col.get("null_pct", 0.0))
        if null_pct >= null_critical_pct:
            alerts.append(
                {
                    "level": AlertLevel.CRITICAL,
                    "column": name,
                    "message": f"{name} null rate {null_pct:.1f}% exceeds critical threshold",
                }
            )
        elif null_pct >= null_warn_pct:
            alerts.append(
                {
                    "level": AlertLevel.WARN,
                    "column": name,
                    "message": f"{name} null rate {null_pct:.1f}% is elevated",
                }
            )

        cardinality = int(col.get("cardinality", 0))
        row_count = int(col.get("row_count", 1)) or 1
        if cardinality == row_count and col.get("dtype") == "object":
            alerts.append(
                {
                    "level": AlertLevel.INFO,
                    "column": name,
                    "message": f"{name} appears identifier-like (cardinality == row count)",
                }
            )

    return alerts
