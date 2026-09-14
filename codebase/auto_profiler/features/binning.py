"""Quantile binning with stability hash for SQL CASE export."""

from __future__ import annotations

import hashlib
import json

import numpy as np
import pandas as pd


def _stability_hash(payload: dict[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def quantile_bins(
    series: pd.Series,
    *,
    n_bins: int = 5,
    column_name: str | None = None,
) -> dict[str, object]:
    """Compute quantile bin edges and labels for numeric columns."""
    name = column_name or str(series.name)
    clean = series.dropna()
    if clean.empty or not pd.api.types.is_numeric_dtype(series):
        return {"column": name, "supported": False, "reason": "non_numeric_or_empty"}

    edges = np.unique(np.quantile(clean, np.linspace(0, 1, n_bins + 1)))
    if len(edges) < 2:
        return {"column": name, "supported": False, "reason": "insufficient_variance"}

    labels = [f"Q{i + 1}" for i in range(len(edges) - 1)]
    binned = pd.cut(series, bins=edges, labels=labels, include_lowest=True, duplicates="drop")
    counts = binned.value_counts(dropna=False).sort_index()

    payload = {
        "column": name,
        "n_bins": len(edges) - 1,
        "edges": [round(float(e), 6) for e in edges],
        "labels": labels,
        "counts": {str(k): int(v) for k, v in counts.items()},
    }
    payload["stability_hash"] = _stability_hash(
        {"column": name, "edges": payload["edges"], "labels": labels}
    )
    payload["supported"] = True
    return payload


def bin_all_numeric(df: pd.DataFrame, *, n_bins: int = 5) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for col in df.select_dtypes(include="number").columns:
        results.append(quantile_bins(df[col], n_bins=n_bins, column_name=str(col)))
    return results
