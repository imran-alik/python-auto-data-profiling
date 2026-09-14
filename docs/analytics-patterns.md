# Analytics Patterns

Patterns demonstrated in this portfolio profiler.

## 1. Null rate profiling

Every column gets `null_count` and `null_pct`. Alerts fire at 20% (warn) and 50% (critical).

**Use when:** initial EDA on unknown CSV landing zones.

## 2. Cardinality vs row count

Flag identifier-like string columns where `cardinality == row_count`.

**Use when:** detecting leaky ID columns before modeling.

## 3. Correlation screening

Numeric pairs with `|r| >= threshold` (default 0.5) surface multicollinearity candidates.

**Use when:** shortlisting features for linear models or SQL feature stores.

## 4. Quantile binning with stability hash

Bin edges derived from `numpy.quantile`. SHA-256 hash of `(column, edges, labels)` enables **reproducible** warehouse CASE statements across re-runs.

**Use when:** exporting Python EDA decisions to dbt/SQL pipelines.

## 5. SQL CASE handoff

`generate_case_sql()` produces copy-paste `CASE` blocks for BigQuery, Snowflake, Postgres.

## 6. Medallion profiling layers

| Layer | Question answered |
|---|---|
| Bronze | What does raw data look like? |
| Silver | Does it pass health guardrails? |
| Gold | What features should we engineer? |

## 7. Evidence index (not blob storage)

`profile_report_index.json` stores **paths** to HTML reports — keeps git lean while preserving audit trail.
