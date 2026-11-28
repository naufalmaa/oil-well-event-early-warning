"""Stage 2 · Find and read 3W instances.

One 3W *instance* = one Parquet file = one well over a few hours at 1 Hz.
The folder name is the event type (0-9); the file name tells the source:
  real       WELL-00014_20170917140000.parquet  (well id + start time)
  simulated  SIMULATED_00072.parquet
  drawn      DRAWN_00007.parquet
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DEFAULT_ROOT = Path("data/raw/3w")
LABEL_COLS = ["class", "state"]


def _source(stem: str) -> str:
    if stem.startswith("WELL-"):
        return "real"
    if stem.startswith("SIMULATED"):
        return "simulated"
    if stem.startswith("DRAWN"):
        return "drawn"
    return "unknown"


def build_index(root: str | Path = DEFAULT_ROOT) -> pd.DataFrame:
    """One row per instance file. Does not open the Parquet files (fast)."""
    rows = []
    for p in sorted(Path(root).glob("*/*.parquet")):
        stem = p.stem
        source = _source(stem)
        well_id, start_time = None, pd.NaT
        if source == "real":
            well_id, ts = stem.split("_", 1)
            start_time = pd.to_datetime(ts, format="%Y%m%d%H%M%S", errors="coerce")
        rows.append(
            {
                "instance_id": f"{p.parent.name}/{stem}",  # sim/drawn ids restart per folder
                "path": str(p),
                "event": int(p.parent.name),
                "source": source,
                "well_id": well_id,
                "start_time": start_time,
            }
        )
    return pd.DataFrame(rows)


def read_instance(path: str | Path, columns: list[str] | None = None) -> pd.DataFrame:
    """Read one instance. Index = timestamp (1 Hz). `columns=None` reads everything."""
    frame = pd.read_parquet(path, columns=columns)
    if "timestamp" in frame.columns:  # some writers keep it as a column
        frame = frame.set_index("timestamp")
    frame.index = pd.to_datetime(frame.index)
    return frame.sort_index()
