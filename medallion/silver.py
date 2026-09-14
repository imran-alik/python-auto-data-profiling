"""Silver layer: cleaned stats with health and guardrails."""

from __future__ import annotations


def describe_silver() -> dict[str, str]:
    return {
        "layer": "silver",
        "purpose": "Health-scored stats after guardrail evaluation",
        "output": "medallion/output/silver_cleaned_stats.json",
    }
