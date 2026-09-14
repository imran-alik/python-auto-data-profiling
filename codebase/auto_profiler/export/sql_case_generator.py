"""Generate SQL CASE expressions from quantile bin definitions."""

from __future__ import annotations


def generate_case_sql(bin_spec: dict[str, object], *, table_alias: str = "") -> str:
    """Build a SQL CASE statement from quantile bin edges."""
    if not bin_spec.get("supported"):
        return f"-- unsupported: {bin_spec.get('reason', 'unknown')}"

    column = str(bin_spec["column"])
    prefix = f"{table_alias}." if table_alias else ""
    ref = f"{prefix}{column}"
    edges: list[float] = bin_spec["edges"]  # type: ignore[assignment]
    labels: list[str] = bin_spec["labels"]  # type: ignore[assignment]

    lines = ["CASE"]
    for i, label in enumerate(labels):
        lower = edges[i]
        upper = edges[i + 1]
        if i == 0:
            lines.append(f"  WHEN {ref} <= {upper} THEN '{label}'")
        elif i == len(labels) - 1:
            lines.append(f"  WHEN {ref} > {lower} THEN '{label}'")
        else:
            lines.append(f"  WHEN {ref} > {lower} AND {ref} <= {upper} THEN '{label}'")
    lines.append("  ELSE NULL")
    lines.append("END")
    return "\n".join(lines)


def generate_all_case_sql(
    bin_specs: list[dict[str, object]],
    *,
    table_alias: str = "",
) -> dict[str, str]:
    return {
        str(spec["column"]): generate_case_sql(spec, table_alias=table_alias)
        for spec in bin_specs
        if spec.get("supported")
    }
