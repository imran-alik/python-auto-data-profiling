#!/usr/bin/env python
"""Generate synthetic telco-style feature sample (~500 rows, no PII)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data" / "source" / "samples" / "telco_features_sample.csv"


def generate_telco_sample(n_rows: int = 500, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    customer_id = [f"SYN-{i:05d}" for i in range(1, n_rows + 1)]
    tenure_months = rng.integers(1, 72, size=n_rows)
    monthly_charges = np.round(rng.uniform(20, 120, size=n_rows), 2)
    total_charges = np.round(monthly_charges * tenure_months * rng.uniform(0.85, 1.05, size=n_rows), 2)
    data_usage_gb = np.round(rng.exponential(15, size=n_rows), 2)
    contract_type = rng.choice(["Month-to-month", "One year", "Two year"], size=n_rows, p=[0.5, 0.3, 0.2])
    payment_method = rng.choice(["Electronic check", "Mailed check", "Bank transfer", "Credit card"], size=n_rows)
    churn = rng.choice([0, 1], size=n_rows, p=[0.73, 0.27])

    # Inject controlled nulls for profiling demos
    data_usage_gb[:5] = np.nan
    payment_method[10:13] = None

    return pd.DataFrame(
        {
            "customer_id": customer_id,
            "tenure_months": tenure_months,
            "monthly_charges": monthly_charges,
            "total_charges": total_charges,
            "data_usage_gb": data_usage_gb,
            "contract_type": contract_type,
            "payment_method": payment_method,
            "churn": churn,
        }
    )


def main() -> int:
    n_rows = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    df = generate_telco_sample(n_rows=n_rows)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(df)} rows to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
