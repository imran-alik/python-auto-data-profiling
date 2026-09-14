"""Bronze layer: raw profile statistics."""

from __future__ import annotations


def describe_bronze() -> dict[str, str]:
    return {
        "layer": "bronze",
        "purpose": "Raw column stats, nulls, cardinality, dtypes from source CSV",
        "output": "medallion/output/bronze_profile.json",
    }
