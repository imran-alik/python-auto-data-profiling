# Data Dictionary — Python Auto Data Profiling

Synthetic telco-style feature sample for portfolio profiling. No PII.

## Entity-relationship diagrams (ERD)

| Diagram | Description |
|---|---|
| **[docs/diagrams/DATA-MODEL.md](docs/diagrams/DATA-MODEL.md)** | Source features, profiling outputs, bin → SQL CASE lineage |
| [DESIGN.md](docs/DESIGN.md) | ASK → SOLUTION → CODE proof |

---

## Source: `telco_features_sample.csv`

| Column | Type | Nullable | Description |
|---|---|---|---|
| `customer_id` | string | no | Surrogate customer key |
| `segment` | string | no | `Consumer`, `SMB`, `Enterprise` |
| `tenure_months` | integer | no | Account tenure |
| `monthly_charges` | float | no | Monthly bill amount |
| `total_charges` | float | no | Lifetime charges |
| `data_usage_gb` | float | no | Monthly data usage |
| `contract_type` | string | no | `Month-to-month`, `One year`, `Two year` |
| `churn` | integer | no | Binary label (0/1) for FE demos |

**Grain:** one row = one customer feature vector.

---

## Profiling outputs (medallion/output/)

| File | Layer | Contents |
|---|---|---|
| `bronze_profile.json` | Bronze | Raw column stats, nulls, cardinality |
| `silver_cleaned_stats.json` | Silver | Health score + guardrail results |
| `gold_feature_recommendations.json` | Gold | Suggested FE actions per column |

**ERD:** [docs/diagrams/DATA-MODEL.md](docs/diagrams/DATA-MODEL.md)
