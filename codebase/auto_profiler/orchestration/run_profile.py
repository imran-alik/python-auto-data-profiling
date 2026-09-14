"""End-to-end profiling orchestration."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from auto_profiler.config.settings import ProfilerConfig
from auto_profiler.export.sql_case_generator import generate_all_case_sql
from auto_profiler.features.binning import bin_all_numeric
from auto_profiler.ingestion.csv_reader import CsvReader
from auto_profiler.profiling.stats_engine import build_profile_stats
from auto_profiler.visualizations.html_report import render_html_report
from profiler_core import (
    build_alerts,
    compute_freshness,
    compute_health_score,
    evaluate_guardrails,
    run_failure_checks,
)


def _write_medallion_layers(
    config: ProfilerConfig,
    *,
    raw_stats: dict[str, object],
    cleaned_stats: dict[str, object],
    recommendations: list[dict[str, object]],
) -> dict[str, str]:
    base = config.medallion_dir
    bronze = base / "bronze_profile.json"
    silver = base / "silver_cleaned_stats.json"
    gold = base / "gold_feature_recommendations.json"

    bronze.write_text(json.dumps(raw_stats, indent=2, default=str), encoding="utf-8")
    silver.write_text(json.dumps(cleaned_stats, indent=2, default=str), encoding="utf-8")
    gold.write_text(json.dumps(recommendations, indent=2, default=str), encoding="utf-8")

    return {
        "bronze": str(bronze.relative_to(config.medallion_dir.parent.parent)),
        "silver": str(silver.relative_to(config.medallion_dir.parent.parent)),
        "gold": str(gold.relative_to(config.medallion_dir.parent.parent)),
    }


def _feature_recommendations(
    columns: list[dict[str, object]],
    correlations: list[dict[str, object]],
) -> list[dict[str, object]]:
    recs: list[dict[str, object]] = []
    for col in columns:
        name = str(col["name"])
        if float(col.get("null_pct", 0)) > 30:
            recs.append({"column": name, "action": "impute_or_drop", "reason": "high_null_rate"})
        if int(col.get("cardinality", 0)) <= 10 and col.get("dtype") == "object":
            recs.append({"column": name, "action": "one_hot_encode", "reason": "low_cardinality_categorical"})
        if col.get("dtype", "").startswith(("int", "float")):
            recs.append({"column": name, "action": "quantile_bin", "reason": "numeric_feature"})

    for pair in correlations[:5]:
        recs.append(
            {
                "columns": [pair["column_a"], pair["column_b"]],
                "action": "review_multicollinearity",
                "correlation": pair["correlation"],
            }
        )
    return recs


def _update_evidence_index(evidence_dir: Path, entry: dict[str, object]) -> Path:
    index_path = evidence_dir / "profile_report_index.json"
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
    else:
        index = {"reports": []}

    reports = index.get("reports", [])
    if not isinstance(reports, list):
        reports = []
    reports.append(entry)
    index["reports"] = reports
    index["latest"] = entry
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    return index_path


def run_profile(config: ProfilerConfig | None = None) -> dict[str, object]:
    """Execute a full profiling run and return summary metadata."""
    cfg = config or ProfilerConfig()
    cfg.ensure_dirs()

    reader = CsvReader(cfg.source_csv)
    df = reader.read()
    source_meta = reader.profile_source()
    freshness = compute_freshness(cfg.source_csv)

    failures = run_failure_checks(df)
    if not failures["passed"]:
        raise ValueError(f"Failure checks failed: {failures['issues']}")

    profile_stats = build_profile_stats(df, correlation_threshold=cfg.correlation_threshold)
    columns = profile_stats["columns"]
    if not isinstance(columns, list):
        columns = []

    health = compute_health_score(columns)
    alerts = build_alerts(columns)
    guardrails = evaluate_guardrails(
        profile_stats, min_rows=cfg.min_rows, max_null_pct=cfg.max_null_pct
    )
    bin_specs = bin_all_numeric(df, n_bins=cfg.quantile_bins)
    sql_cases = generate_all_case_sql(bin_specs)

    cleaned_stats = {
        **profile_stats,
        "health": health,
        "guardrails_passed": guardrails["passed"],
    }
    recommendations = _feature_recommendations(columns, profile_stats.get("correlations", []))  # type: ignore[arg-type]

    timestamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    report_name = f"profile_report_{cfg.run_name}_{timestamp}.html"
    report_path = cfg.report_output_dir / report_name

    render_html_report(
        df,
        profile_stats,
        health=health,
        alerts=alerts,
        bin_specs=bin_specs,
        output_path=report_path,
        run_name=cfg.run_name,
    )

    medallion_paths = _write_medallion_layers(
        cfg,
        raw_stats=profile_stats,
        cleaned_stats=cleaned_stats,
        recommendations=recommendations,
    )

    summary: dict[str, object] = {
        "run_name": cfg.run_name,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "source": source_meta,
        "freshness": freshness,
        "row_count": profile_stats["row_count"],
        "column_count": profile_stats["column_count"],
        "health_score": health["score"],
        "alert_count": len(alerts),
        "guardrails": guardrails,
        "report_path": str(report_path.relative_to(cfg.report_output_dir.parent)).replace("\\", "/"),
        "medallion": medallion_paths,
        "sql_case_columns": list(sql_cases.keys()),
    }

    rel_report = summary["report_path"]
    _update_evidence_index(
        cfg.evidence_dir,
        {
            "run_name": cfg.run_name,
            "generated_at_utc": summary["generated_at_utc"],
            "report_path": rel_report,
            "health_score": health["score"],
            "row_count": profile_stats["row_count"],
        },
    )

    sidecar = cfg.evidence_dir / f"run_summary_{cfg.run_name}_{timestamp}.json"
    sidecar.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    summary["evidence_sidecar"] = str(sidecar.relative_to(cfg.evidence_dir.parent)).replace("\\", "/")

    return summary
