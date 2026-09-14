# Compliance & Data Sharing Policy

## Portfolio case study — not production

This repository is a **portfolio demonstration** of Python-native auto data profiling and feature engineering. It does **not** contain production datasets, credentials, or customer information.

## Redacted design of private work

Concepts in `docs/DESIGN.md` are **redacted abstractions** inspired by private enterprise repositories. Specific table names, business rules, IAM bindings, and internal pipeline identifiers from those repos are **not** reproduced here.

## Full-scale sharing prohibited

Under compliance obligations from prior employers and client agreements:

- **No** full-scale production data exports
- **No** real customer identifiers, phone numbers, or billing records
- **No** internal connection strings, API keys, or service account JSON
- **No** verbatim copy of proprietary SQL or dbt models from private repos

## Synthetic samples only

All committed CSV data under `data/source/samples/` is **synthetically generated** (`codebase/scripts/generate_sample.py`) with:

- Fake `SYN-xxxxx` customer IDs
- Randomized numeric features
- Controlled null injections for profiling demos
- Zero PII

## Evidence artifacts

`data/evidence/` stores **JSON indexes and run summaries** — not raw HTML report blobs. HTML reports are generated locally under `visualizations/` and referenced by path in the index.

## Credential placeholders

`env/.env.example` contains **placeholder names only**. Never commit real secrets.

## Reviewer guidance

If you need to validate behavior, run:

```powershell
python codebase/scripts/certify_profile_run.py
```

Quality gates in the certification output confirm row counts, guardrails, and report generation on synthetic data.
