# Handover — Python Auto Data Profiling

## What this is

Portfolio case study: Python-native auto EDA + feature-engineering profiler. Inspired by [R-Auto-Data-Profiling](https://github.com/rao-anas-riaz/R-Auto-Data-Profiling).

## Run locally

```powershell
.\codebase\scripts\bootstrap.ps1
```

Certification:

```powershell
python codebase/scripts/certify_profile_run.py
```

## Key paths

| Path | Purpose |
|---|---|
| `codebase/auto_profiler/orchestration/run_profile.py` | Main entry |
| `packages/profiler_core/` | Reusable guardrails |
| `data/evidence/profile_report_index.json` | Latest report path index |
| `visualizations/` | Generated HTML (gitignored except `.gitkeep`) |
| `docs/DESIGN.md` | Full design with verdicts |

## Tests & lint

```powershell
pytest tests/ -q
ruff check codebase packages tests
```

## Docker

```powershell
docker compose -f docker/docker-compose.yml up --build
```

## Compliance reminder

- Synthetic data only — see `COMPLIANCE.md`
- No real credentials in `env/.env.example`
- Do not commit production CSVs or full HTML reports

## Next steps (optional)

- Add Great Expectations or Pandera validation layer
- Support Parquet ingestion
- Embed mini demo HTML in repo for GitHub Pages
