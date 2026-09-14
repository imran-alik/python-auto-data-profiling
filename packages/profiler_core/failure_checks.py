"""Structural failure checks before profiling."""

from __future__ import annotations

import pandas as pd


def run_failure_checks(df: pd.DataFrame) -> dict[str, object]:
    """Detect empty frames, duplicate column names, and all-null columns."""
    issues: list[str] = []

    if df.empty:
        issues.append("empty_dataframe")

    if df.columns.duplicated().any():
        dupes = df.columns[df.columns.duplicated()].tolist()
        issues.append(f"duplicate_columns:{dupes}")

    all_null_cols = [c for c in df.columns if df[c].isna().all()]
    if all_null_cols:
        issues.append(f"all_null_columns:{all_null_cols}")

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "row_count": len(df),
        "column_count": len(df.columns),
    }
