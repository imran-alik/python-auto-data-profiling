# Design Document — Python Auto Data Profiling

| Field | Value |
|---|---|
| **Status** | Implemented (portfolio case study) |
| **Inspiration** | [R-Auto-Data-Profiling](https://github.com/rao-anas-riaz/R-Auto-Data-Profiling) |
| **Code root** | `codebase/auto_profiler/` |
| **Reusable core** | `packages/profiler_core/` |
| **Data root** | `data/source/samples/` (synthetic) · `visualizations/` (HTML output) |
| **Entry points** | `run_profile.py`, `certify_profile_run.py` |
| **Date** | 2026-09-14 |
| **Version** | 1.0.0 |

---

## 0. Verdicts

| # | Requirement | Verdict | Proof |
|---|---|---|---|
| V1 | Column null/cardinality/dtype stats | **Proven** | `test_build_profile_stats_counts` |
| V2 | Correlation detection | **Proven** | `test_correlations_detected` |
| V3 | Quantile binning + stability hash | **Proven** | `test_stability_hash_deterministic` |
| V4 | SQL CASE export | **Proven** | `test_generate_case_sql` |
| V5 | Interactive HTML report | **Proven** | `test_render_html_report_creates_file` |
| V6 | End-to-end orchestration | **Proven** | `certify_profile_run.py` quality gates |
| V7 | Medallion layers | **Proven** | bronze/silver/gold JSON under `medallion/output/` |
| V8 | Compliance (synthetic only) | **Documented** | `COMPLIANCE.md` |

---

## 0.1 Data model & ERD

Source feature table → profiling outputs → bin specs → SQL CASE export. Diagram style reference: [uber-data-engineering-mage-project/data_model](https://github.com/darshilparmar/uber-data-engineering-mage-project/blob/main/data_model.jpeg).

| Artifact | Path |
|---|---|
| Full ERD + lineage | [docs/diagrams/DATA-MODEL.md](diagrams/DATA-MODEL.md) |
| Column dictionary | [data-dictionary.md](../data-dictionary.md) |

---

## 1. Problem statement

### 1.1 Business problem

Data engineers and ML practitioners need **fast, reproducible EDA** that bridges exploration and feature engineering — especially when translating Python discoveries into warehouse SQL.

### 1.2 Technical problem

Build a **Python-native** profiler (evolved from R Auto EDA) that:

1. Profiles CSV samples with nulls, cardinality, dtypes, correlations
2. Produces quantile bins with deterministic stability hashes
3. Exports SQL `CASE` expressions for warehouse handoff
4. Renders standalone interactive HTML (Plotly CDN, no server)
5. Uses synthetic portfolio data only (compliance)

---

## 2. Ask register

| ID | Ask | Solution | Code | Expected output |
|---|---|---|---|---|
| **A1** | Ingest synthetic CSV | `CsvReader` | `ingestion/csv_reader.py` | pandas DataFrame |
| **A2** | Column stats | `build_profile_stats` | `profiling/stats_engine.py` | JSON column metrics |
| **A3** | Quantile bins | `bin_all_numeric` | `features/binning.py` | edges + stability_hash |
| **A4** | SQL CASE export | `generate_all_case_sql` | `export/sql_case_generator.py` | SQL strings per column |
| **A5** | HTML report | `render_html_report` | `visualizations/html_report.py` | `.html` under `visualizations/` |
| **A6** | Guardrails | `profiler_core` | `packages/profiler_core/` | pass/fail + alerts |
| **A7** | Evidence index | `_update_evidence_index` | `orchestration/run_profile.py` | `profile_report_index.json` |

---

## 3. Source schema (synthetic telco sample)

| Column | Type | Notes |
|---|---|---|
| `customer_id` | string | `SYN-xxxxx` synthetic ID |
| `tenure_months` | int | 1–72 |
| `monthly_charges` | float | USD-like |
| `total_charges` | float | derived |
| `data_usage_gb` | float | ~5 nulls injected |
| `contract_type` | categorical | 3 levels |
| `payment_method` | categorical | ~3 nulls injected |
| `churn` | int (0/1) | target-like |

**Grain:** one row per synthetic customer · **PII:** none

---

## 4. Medallion outputs

| Layer | File | Content |
|---|---|---|
| Bronze | `medallion/output/bronze_profile.json` | Raw profile stats |
| Silver | `medallion/output/silver_cleaned_stats.json` | Stats + health + guardrails |
| Gold | `medallion/output/gold_feature_recommendations.json` | Binning/encoding/multicollinearity recs |

---

## 5. Failure matrix

| Node | Failure | Detection | Mitigation |
|---|---|---|---|
| CSV read | File missing | `FileNotFoundError` | Run `generate_sample.py` |
| Empty frame | 0 rows | `run_failure_checks` | Abort run |
| All-null column | 100% nulls | `failure_checks` + alerts | Flag in HTML |
| Single numeric col | No correlation heatmap | `compute_correlations` returns [] | HTML fallback message |
| High null rate | >40% | `evaluate_guardrails` | Violation in certification |

---

## 6. Connectivity matrix

| Component | Connects to | Disconnect behavior |
|---|---|---|
| `CsvReader` | Local CSV | Raises if missing |
| `html_report` | Plotly CDN | Offline: charts fail to render (report shell loads) |
| Docker | Volume mounts | Falls back to baked-in sample CSV |
| `env/.env` | Optional overrides | Defaults from `ProfilerConfig` |

---

## 7. Data evolution

| Version | Change |
|---|---|
| 1.0.0 | Initial synthetic telco sample, 8 columns, ~500 rows |
| Future | Additional sample generators (retail, logs) — synthetic only |
