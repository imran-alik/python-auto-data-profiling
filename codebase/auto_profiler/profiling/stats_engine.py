"""Column-level statistics: nulls, cardinality, dtypes, correlations."""

from __future__ import annotations

import pandas as pd


def _column_stat(name: str, series: pd.Series, row_count: int) -> dict[str, object]:
    null_count = int(series.isna().sum())
    null_pct = round(100.0 * null_count / row_count, 2) if row_count else 0.0
    cardinality = int(series.nunique(dropna=True))
    stat: dict[str, object] = {
        "name": name,
        "dtype": str(series.dtype),
        "null_count": null_count,
        "null_pct": null_pct,
        "cardinality": cardinality,
        "row_count": row_count,
    }
    if pd.api.types.is_numeric_dtype(series):
        desc = series.describe()
        stat["min"] = float(desc["min"]) if pd.notna(desc["min"]) else None
        stat["max"] = float(desc["max"]) if pd.notna(desc["max"]) else None
        stat["mean"] = round(float(desc["mean"]), 4) if pd.notna(desc["mean"]) else None
        stat["std"] = round(float(desc["std"]), 4) if pd.notna(desc["std"]) else None
    return stat


def compute_column_stats(df: pd.DataFrame) -> list[dict[str, object]]:
    row_count = len(df)
    return [_column_stat(str(col), df[col], row_count) for col in df.columns]


def compute_correlations(
    df: pd.DataFrame,
    *,
    threshold: float = 0.5,
) -> list[dict[str, object]]:
    numeric = df.select_dtypes(include="number")
    if numeric.shape[1] < 2:
        return []

    corr = numeric.corr(numeric_only=True)
    pairs: list[dict[str, object]] = []
    cols = list(corr.columns)
    for i, col_a in enumerate(cols):
        for col_b in cols[i + 1 :]:
            value = corr.loc[col_a, col_b]
            if pd.isna(value):
                continue
            abs_val = abs(float(value))
            if abs_val >= threshold:
                pairs.append(
                    {
                        "column_a": col_a,
                        "column_b": col_b,
                        "correlation": round(float(value), 4),
                        "abs_correlation": round(abs_val, 4),
                    }
                )
    pairs.sort(key=lambda p: p["abs_correlation"], reverse=True)
    return pairs


def build_profile_stats(df: pd.DataFrame, *, correlation_threshold: float = 0.5) -> dict[str, object]:
    columns = compute_column_stats(df)
    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": columns,
        "correlations": compute_correlations(df, threshold=correlation_threshold),
    }
