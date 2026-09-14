"""Gold layer: feature-engineering recommendations."""

from __future__ import annotations


def describe_gold() -> dict[str, str]:
    return {
        "layer": "gold",
        "purpose": "Actionable feature recommendations (binning, encoding, multicollinearity)",
        "output": "medallion/output/gold_feature_recommendations.json",
    }
