"""Stage 3→6 bridge · 1 Hz instance → 1-minute frame.

Every statistic for minute t uses only seconds inside [t, t+1min). The label of
the minute is the label at its *last* second, i.e. what is true when the
prediction for that minute is made. No value from a later minute is used.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .load import read_instance


def to_minutes(df: pd.DataFrame, variables: list[str], freq: str = "1min") -> pd.DataFrame:
    """Aggregate one instance to `freq` with mean/std/last per variable + labels."""
    present = [v for v in variables if v in df.columns]
    g = df[present].resample(freq, label="left", closed="left")
    out = pd.concat({"mean": g.mean(), "std": g.std(), "last": g.last()}, axis=1)
    out.columns = [f"{var}__{stat}" for stat, var in out.columns]  # e.g. P-TPT__mean
    labels = df[["class"]].resample(freq, label="left", closed="left").last()
    out["label"] = labels["class"]
    # y: 1 = transient (1xx) or event (1-9); 0 = normal; NaN = unknown (dropped later)
    out["y"] = np.where(out["label"].isna(), np.nan, (out["label"] > 0).astype(float))
    return out


def prepare(index: pd.DataFrame, variables: list[str], freq: str = "1min") -> pd.DataFrame:
    """Process all instances in `index` into one long per-minute table."""
    frames = []
    for row in index.itertuples(index=False):
        raw = read_instance(row.path, columns=[*variables, "class"])
        m = to_minutes(raw, variables, freq)
        m["instance_id"] = row.instance_id
        m["event"] = row.event
        m["source"] = row.source
        m["well_id"] = row.well_id
        frames.append(m)
    out = pd.concat(frames)
    out.index.name = "minute"
    return out.reset_index()
