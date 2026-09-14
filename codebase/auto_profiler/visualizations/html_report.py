"""Interactive HTML report generation (Plotly, no server required)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go


def _null_bar_figure(columns: list[dict[str, object]]) -> go.Figure:
    names = [str(c["name"]) for c in columns]
    nulls = [float(c["null_pct"]) for c in columns]
    fig = go.Figure(go.Bar(x=names, y=nulls, marker_color="#e45756"))
    fig.update_layout(title="Null % by Column", yaxis_title="Null %", template="plotly_white")
    return fig


def _cardinality_figure(columns: list[dict[str, object]]) -> go.Figure:
    names = [str(c["name"]) for c in columns]
    card = [int(c["cardinality"]) for c in columns]
    fig = go.Figure(go.Bar(x=names, y=card, marker_color="#4c78a8"))
    fig.update_layout(title="Cardinality by Column", yaxis_title="Distinct Count", template="plotly_white")
    return fig


def _correlation_heatmap(df: pd.DataFrame) -> go.Figure | None:
    numeric = df.select_dtypes(include="number")
    if numeric.shape[1] < 2:
        return None
    corr = numeric.corr(numeric_only=True)
    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=list(corr.columns),
            y=list(corr.index),
            colorscale="RdBu",
            zmid=0,
        )
    )
    fig.update_layout(title="Numeric Correlation Heatmap", template="plotly_white")
    return fig


def _distribution_figure(df: pd.DataFrame, column: str) -> go.Figure | None:
    if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return None
    fig = go.Figure(go.Histogram(x=df[column].dropna(), nbinsx=20, marker_color="#72b7b2"))
    fig.update_layout(title=f"Distribution: {column}", template="plotly_white")
    return fig


def _fig_to_div(fig: go.Figure, div_id: str) -> str:
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id=div_id)


def render_html_report(
    df: pd.DataFrame,
    profile_stats: dict[str, object],
    *,
    health: dict[str, float | int],
    alerts: list[dict[str, str]],
    bin_specs: list[dict[str, object]],
    output_path: Path,
    run_name: str,
) -> Path:
    """Write a self-contained interactive HTML report."""
    columns = profile_stats.get("columns", [])
    if not isinstance(columns, list):
        columns = []

    null_fig = _null_bar_figure(columns)
    card_fig = _cardinality_figure(columns)
    corr_fig = _correlation_heatmap(df)

    numeric_cols = [str(c["name"]) for c in columns if c.get("dtype", "").startswith(("int", "float"))]
    dist_divs: list[str] = []
    for i, col in enumerate(numeric_cols[:3]):
        dist = _distribution_figure(df, col)
        if dist is not None:
            dist_divs.append(_fig_to_div(dist, f"dist_{i}"))

    alert_rows = "".join(
        f"<tr><td>{a['level']}</td><td>{a['column']}</td><td>{a['message']}</td></tr>"
        for a in alerts
    ) or "<tr><td colspan='3'>No alerts</td></tr>"

    bin_rows = "".join(
        f"<tr><td>{b.get('column')}</td><td>{b.get('stability_hash', '—')}</td>"
        f"<td>{b.get('n_bins', '—')}</td></tr>"
        for b in bin_specs
        if b.get("supported")
    ) or "<tr><td colspan='3'>No numeric bins</td></tr>"

    generated_at = datetime.now(tz=UTC).isoformat()
    corr_div = _fig_to_div(corr_fig, "corr") if corr_fig else "<p>No correlation heatmap (need 2+ numeric columns)</p>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Auto Profile Report — {run_name}</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #fafafa; color: #222; }}
    h1, h2 {{ color: #1a1a2e; }}
    .card {{ background: #fff; border-radius: 8px; padding: 1rem 1.5rem; margin-bottom: 1.5rem;
             box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; }}
    th {{ background: #f0f0f0; }}
    .kpi {{ display: inline-block; margin-right: 2rem; }}
    .kpi strong {{ font-size: 1.4rem; }}
  </style>
</head>
<body>
  <h1>Python Auto Data Profiling</h1>
  <p>Run: <code>{run_name}</code> · Generated: {generated_at}</p>

  <div class="card">
    <div class="kpi"><strong>{profile_stats.get('row_count', 0)}</strong><br/>Rows</div>
    <div class="kpi"><strong>{profile_stats.get('column_count', 0)}</strong><br/>Columns</div>
    <div class="kpi"><strong>{health.get('score', 0)}</strong><br/>Health Score</div>
  </div>

  <div class="card">
    <h2>Null Rates</h2>
    {_fig_to_div(null_fig, "nulls")}
  </div>

  <div class="card">
    <h2>Cardinality</h2>
    {_fig_to_div(card_fig, "cardinality")}
  </div>

  <div class="card">
    <h2>Correlations</h2>
    {corr_div}
  </div>

  <div class="card">
    <h2>Distributions (sample numeric columns)</h2>
    {"".join(dist_divs)}
  </div>

  <div class="card">
    <h2>Alerts</h2>
    <table><thead><tr><th>Level</th><th>Column</th><th>Message</th></tr></thead>
    <tbody>{alert_rows}</tbody></table>
  </div>

  <div class="card">
    <h2>Feature Binning (stability hash)</h2>
    <table><thead><tr><th>Column</th><th>Hash</th><th>Bins</th></tr></thead>
    <tbody>{bin_rows}</tbody></table>
  </div>

  <div class="card">
    <h2>Profile JSON (embedded)</h2>
    <pre>{json.dumps(profile_stats, indent=2, default=str)}</pre>
  </div>
</body>
</html>
"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path
