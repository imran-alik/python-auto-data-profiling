"""Dataset freshness signals for portfolio profiling runs."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path


def compute_freshness(source_path: Path, *, now: datetime | None = None) -> dict[str, object]:
    """Return file mtime age and a simple freshness label."""
    resolved = Path(source_path).resolve()
    if not resolved.exists():
        return {"exists": False, "age_hours": None, "label": "missing"}

    mtime = datetime.fromtimestamp(resolved.stat().st_mtime, tz=UTC)
    reference = now or datetime.now(tz=UTC)
    age_hours = round((reference - mtime).total_seconds() / 3600, 2)

    if age_hours <= 24:
        label = "fresh"
    elif age_hours <= 168:
        label = "stale"
    else:
        label = "aged"

    return {
        "exists": True,
        "path": str(resolved),
        "modified_at_utc": mtime.isoformat(),
        "age_hours": age_hours,
        "label": label,
    }
