# Data Model & ERD — Python Auto Data Profiling

Feature-engineering profiler: source CSV → stats → bins → SQL CASE export.

Inspired by [R-Auto-Data-Profiling](https://github.com/rao-anas-riaz/R-Auto-Data-Profiling); diagram style reference: [uber-data-engineering-mage-project](https://github.com/darshilparmar/uber-data-engineering-mage-project).

Cross-reference: [data-dictionary.md](../../data-dictionary.md) · [DESIGN.md](../DESIGN.md)

---

## 1. Source sample ERD

Synthetic telco-style feature table (`telco_features_sample.csv`).

```mermaid
erDiagram
    CUSTOMER_FEATURES {
        string customer_id PK
        string segment
        int tenure_months
        float monthly_charges
        float total_charges
        float data_usage_gb
        string contract_type
        int churn "label"
    }
```

**Grain:** one row = one customer feature vector for profiling / binning.

---

## 2. Profiling output model

```mermaid
erDiagram
    SOURCE_CSV ||--|| BRONZE_PROFILE : "raw stats"
    BRONZE_PROFILE ||--|| SILVER_CLEANED_STATS : "health + guardrails"
    SILVER_CLEANED_STATS ||--|| GOLD_FEATURE_RECS : "recommendations"
    SOURCE_CSV ||--o{ BIN_SPECS : "numeric columns"
    BIN_SPECS ||--|| SQL_CASE_EXPORT : "deployable CASE statements"

    BRONZE_PROFILE {
        int row_count
        json column_stats
    }
    SILVER_CLEANED_STATS {
        float health_score
        boolean guardrails_passed
    }
    GOLD_FEATURE_RECS {
        string column
        string action "bin|impute|encode"
    }
    BIN_SPECS {
        string column_name
        json quantile_edges
        string stability_hash
    }
```

---

## 3. Pipeline lineage

```mermaid
flowchart LR
    CSV[telco_features_sample.csv] --> READ[CsvReader]
    READ --> STATS[stats_engine]
    STATS --> HTML[Plotly HTML report]
    STATS --> BIN[features/binning]
    BIN --> SQL[sql_case_generator]
    STATS --> MED[medallion/output JSON]
    HTML --> VIZ[visualizations/]
    MED --> EV[profile_report_index.json]
```
