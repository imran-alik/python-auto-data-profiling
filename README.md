# Python Auto Data Profiling

Python-native auto EDA and feature-engineering profiler with interactive HTML output — a portfolio case study evolved from the R ecosystem.

## Inspiration

This project is inspired by [**R-Auto-Data-Profiling**](https://github.com/rao-anas-riaz/R-Auto-Data-Profiling) by [Rao Anas Riaz](https://github.com/rao-anas-riaz), which demonstrates comprehensive R-based data profiling and interactive report generation.

**Our Python evolution adds:**

- Feature-engineering focus (quantile binning, SQL `CASE` export, stability hashes)
- Reusable `profiler_core` guardrails (freshness, health, alerts)
- Medallion-style outputs (bronze / silver / gold)
- Plotly-powered standalone HTML reports (no server required)
- Synthetic portfolio samples only — see [COMPLIANCE.md](COMPLIANCE.md)

## Quick start

```powershell
cd python-auto-data-profiling
.\codebase\scripts\bootstrap.ps1
```

Or manually:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python codebase/scripts/generate_sample.py
python codebase/scripts/certify_profile_run.py
pytest tests/ -q
```

## Data model (ERD)

Linked dataset diagrams (source → profile → bins → SQL), inspired by [Uber Mage data_model](https://github.com/darshilparmar/uber-data-engineering-mage-project/blob/main/data_model.jpeg):

- **[docs/diagrams/DATA-MODEL.md](docs/diagrams/DATA-MODEL.md)** — full ERD + lineage
- **[data-dictionary.md](data-dictionary.md)** — column definitions

## Project layout

```
python-auto-data-profiling/
├── packages/profiler_core/     # Reusable freshness, health, guardrails
├── codebase/auto_profiler/     # Main profiling package
├── medallion/                  # Bronze / silver / gold layer descriptors
├── data/source/samples/        # Synthetic CSV samples (no PII)
├── data/evidence/              # Run index JSON (not full HTML)
├── visualizations/             # Generated HTML reports (runtime)
├── docker/                     # Containerized profiling
├── docs/                       # DESIGN.md, HANDOVER.md
└── tests/                      # pytest suite
```

## Run a profile

```powershell
python -c "from auto_profiler.orchestration.run_profile import run_profile; print(run_profile())"
```

Open the HTML report path printed in `data/evidence/profile_report_index.json`.

## Docker

```powershell
docker compose -f docker/docker-compose.yml up --build
```

On-prem data mount:

```powershell
docker compose -f docker/docker-compose.onprem.yml up --build
```

## Roadmap (modularity improvements)

| Area | Next step |
|---|---|
| Connectors | Parquet, BigQuery, Snowflake sample readers behind `ingestion/` protocol |
| Drift | Compare two profile runs; highlight column distribution shifts |
| Stability | Rolling bin stability scores across monthly snapshots (R-portfolio parity) |
| Orchestration | Airflow/Databricks task wrapper around `certify_profile_run.py` |
| Packages | Publish `profiler_core` as standalone wheel for other portfolio repos |

## License

Portfolio / educational use. Synthetic data only. See [COMPLIANCE.md](COMPLIANCE.md).
