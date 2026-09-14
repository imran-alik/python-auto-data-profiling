"""CSV ingestion for portfolio profiling samples."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class CsvReader:
    """Read synthetic portfolio CSV samples with basic validation."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def read(self) -> pd.DataFrame:
        if not self.path.exists():
            raise FileNotFoundError(f"Source CSV not found: {self.path}")
        return pd.read_csv(self.path)

    def count_rows(self) -> int:
        df = self.read()
        return len(df)

    def profile_source(self) -> dict[str, object]:
        stat = self.path.stat()
        return {
            "path": str(self.path),
            "size_bytes": stat.st_size,
            "row_count": self.count_rows(),
        }
