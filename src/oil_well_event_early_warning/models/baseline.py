"""Stage 5 · Baseline: trailing z-score rule.

For each instance and each chosen variable, compare the current minute mean to
the mean/std of the PREVIOUS `window` minutes (shift(1) = no look-ahead).
Score = largest |z| over the variables. Alert rule and metrics are shared with
the model (evaluation/events.py). The threshold k is chosen on TRAIN wells only,
as the smallest k that keeps false alarms within the budget.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import cli_config
from ..evaluation.events import apply_alert_rule, false_alarms_per_well_day, summarize


def zscore_score(minutes: pd.DataFrame, variables: list[str], window: int = 60) -> pd.Series:
    scores = []
    for _, g in minutes.groupby("instance_id", sort=False):
        z_abs = []
        for v in variables:
            col = f"{v}__mean"
            if col not in g or g[col].isna().all():
                continue
            prev = g[col].shift(1).rolling(window, min_periods=window // 2)
            z = (g[col] - prev.mean()) / prev.std().replace(0, np.nan)
            z_abs.append(z.abs())
        s = pd.concat(z_abs, axis=1).max(axis=1) if z_abs else pd.Series(np.nan, index=g.index)
        scores.append(s)
    return pd.concat(scores).reindex(minutes.index)


def alerts_for(
    minutes: pd.DataFrame, score: pd.Series, k: float, persistence: int, cooldown: int
) -> pd.Series:
    above = score > k
    return (
        above.groupby(minutes["instance_id"], sort=False, group_keys=False)
        .apply(lambda s: apply_alert_rule(s, persistence, cooldown))
        .reindex(minutes.index)
    )


def choose_k(minutes, score, budget, persistence, cooldown, grid=None) -> float:
    """Smallest k whose false-alarm rate on normal instances is within budget."""
    grid = np.arange(2.0, 15.01, 0.5) if grid is None else grid
    for k in grid:
        m = minutes.assign(alert=alerts_for(minutes, score, k, persistence, cooldown))
        if false_alarms_per_well_day(m) <= budget:
            return float(k)
    return float(grid[-1])


def main() -> None:
    cfg = cli_config(__doc__ or "baseline")
    b, a = cfg["baseline"], cfg["alert"]
    minutes = pd.read_parquet(Path(cfg["paths"]["processed"]) / "minutes.parquet")
    minutes = minutes[minutes["split"].isin(["train", "test"])]
    minutes["score"] = zscore_score(minutes, b["variables"], b["window"])

    train = minutes[minutes["split"] == "train"]
    k = choose_k(train, train["score"], a["budget_per_well_day"], a["persistence"], a["cooldown"])

    results = {"k": k}
    for name, part in minutes.groupby("split"):
        part = part.assign(
            alert=alerts_for(part, part["score"], k, a["persistence"], a["cooldown"])
        )
        results[name] = summarize(part)

    out = Path(cfg["paths"]["reports"]) / "metrics.json"
    metrics = json.loads(out.read_text()) if out.exists() else {}
    metrics["baseline"] = results
    out.write_text(json.dumps(metrics, indent=2, default=float).replace("NaN", "null"))
    print(json.dumps(results, indent=2, default=float))


if __name__ == "__main__":
    main()
