#!/usr/bin/env python
"""Certified portfolio profiling run with quality gates."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODEBASE = ROOT / "codebase"
sys.path.insert(0, str(CODEBASE))
sys.path.insert(0, str(ROOT / "packages"))

from auto_profiler.config.settings import ProfilerConfig, _repo_root
from auto_profiler.ingestion.csv_reader import CsvReader
from auto_profiler.orchestration.run_profile import run_profile


def main() -> int:
    repo = _repo_root()
    csv_path = repo / "data" / "source" / "samples" / "telco_features_sample.csv"
    if not csv_path.exists():
        print("Sample CSV missing; run generate_sample.py first", file=sys.stderr)
        return 1

    source_rows = CsvReader(csv_path).count_rows()
    config = ProfilerConfig(source_csv=csv_path, run_name="telco_sample")
    summary = run_profile(config)

    certification = {
        "problem": "Python-native auto EDA and feature-engineering profiling (portfolio case study)",
        "source": {
            "file": str(csv_path.relative_to(repo)).replace("\\", "/"),
            "source_rows_in_file": source_rows,
            "synthetic": True,
            "pii": False,
        },
        "profile_summary": summary,
        "quality_gates": {
            "source_rows_match_profile": summary["row_count"] == source_rows,
            "health_score_above_zero": float(summary["health_score"]) > 0,
            "guardrails_passed": summary["guardrails"]["passed"],
            "report_path_present": bool(summary.get("report_path")),
            "medallion_layers_written": len(summary.get("medallion", {})) == 3,
            "sql_cases_generated": len(summary.get("sql_case_columns", [])) >= 1,
        },
    }

    print(json.dumps(certification, indent=2, default=str))

    failed = [k for k, v in certification["quality_gates"].items() if not v]
    if failed:
        print(f"QUALITY GATE FAILURES: {failed}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
