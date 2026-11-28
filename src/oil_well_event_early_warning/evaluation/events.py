"""Stage 5/7 · Event-level evaluation (the headline metrics of P1).

Input: one row per (instance, minute) with columns
  instance_id, well_id, event, minute, label, alert (bool)
Definitions (docs/01-problem-framing.md):
  event start   = first minute whose label != 0  (transient 1xx or event 1-9)
  steady start  = first minute whose label is 1-9 (event fully developed)
  detected      = at least one alert between event start and end of instance
  lead time     = steady start - first alert  (minutes, >0 = early)
  detection delay (events 3, 4: no transient) = first alert - event start
  false alarms  = alerts on normal instances (event 0), per well-day
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .metrics import bootstrap_ci

HORIZONS = (1, 5, 15, 30, 60)
NO_TRANSIENT = {3, 4}


def apply_alert_rule(score_above: pd.Series, persistence: int = 3, cooldown: int = 60) -> pd.Series:
    """Turn a per-minute boolean (score > threshold) into alerts for ONE instance.

    An alert fires at minute t if the last `persistence` minutes are all True,
    and no alert fired in the previous `cooldown` minutes.
    """
    above = score_above.fillna(False).to_numpy(dtype=bool)
    alerts = np.zeros_like(above)
    run, last_alert = 0, -(10**9)
    for i, a in enumerate(above):
        run = run + 1 if a else 0
        if run >= persistence and i - last_alert > cooldown:
            alerts[i] = True
            last_alert = i
    return pd.Series(alerts, index=score_above.index)


def per_event_table(minutes: pd.DataFrame) -> pd.DataFrame:
    """One row per event instance (event != 0) with detection, lead time, delay."""
    rows = []
    ev = minutes[minutes["event"] != 0]
    for inst, g in ev.groupby("instance_id", sort=False):
        g = g.sort_values("minute")
        t = (g["minute"] - g["minute"].iloc[0]).dt.total_seconds().to_numpy() / 60
        lab = g["label"].to_numpy()
        alert = g["alert"].to_numpy(dtype=bool)
        abnormal = np.flatnonzero((lab != 0) & ~np.isnan(lab))
        if len(abnormal) == 0:
            continue
        start = t[abnormal[0]]
        steady_idx = np.flatnonzero((lab >= 1) & (lab <= 9))
        steady = t[steady_idx[0]] if len(steady_idx) else np.nan
        after = np.flatnonzero(alert & (t >= start))
        first = t[after[0]] if len(after) else np.nan
        event = int(g["event"].iloc[0])
        rows.append(
            {
                "instance_id": inst,
                "well_id": g["well_id"].iloc[0],
                "event": event,
                "detected": bool(len(after)),
                "lead_time_min": (steady - first)
                if (event not in NO_TRANSIENT and len(after))
                else np.nan,
                "detection_delay_min": (first - start)
                if (event in NO_TRANSIENT and len(after))
                else np.nan,
            }
        )
    return pd.DataFrame(rows)


def false_alarms_per_well_day(minutes: pd.DataFrame) -> float:
    normal = minutes[minutes["event"] == 0]
    days = len(normal) / (60 * 24)  # one row = one minute
    return float(normal["alert"].sum() / days) if days else np.nan


def recall_at_lead(events: pd.DataFrame, horizons=HORIZONS) -> dict[int, float]:
    """Share of transient events alerted at least H minutes before steady state."""
    tr = events[~events["event"].isin(NO_TRANSIENT)]
    if tr.empty:
        return {h: np.nan for h in horizons}
    return {h: float((tr["lead_time_min"] >= h).mean()) for h in horizons}


def _ci(values: pd.Series, groups: pd.Series, stat, n: int = 1000) -> list[float]:
    """95% CI of  over events, resampling whole WELLS (rows of a well are correlated)."""
    ok = values.notna().to_numpy()
    if ok.sum() < 2:
        return [float("nan")] * 3
    v = values.to_numpy(dtype=float)[ok]
    point, lo, hi = bootstrap_ci(
        v, v, lambda a, _b: stat(a), groups=groups.to_numpy()[ok], n_resamples=n
    )
    return [point, lo, hi]


def summarize(minutes: pd.DataFrame, with_ci: bool = True) -> dict:
    events = per_event_table(minutes)
    ci = {}
    if with_ci and len(events):
        ci = {
            "event_recall_ci": _ci(events["detected"].astype(float), events["well_id"], np.mean),
            "median_lead_time_ci": _ci(events["lead_time_min"], events["well_id"], np.median),
        }
    per_event = (
        events.groupby("event")
        .agg(
            n=("detected", "size"),
            recall=("detected", "mean"),
            median_lead=("lead_time_min", "median"),
            median_delay=("detection_delay_min", "median"),
        )
        .round(3)
        .to_dict(orient="index")
    )
    return {
        **ci,
        "per_event": {int(k): v for k, v in per_event.items()},
        "event_recall": float(events["detected"].mean()) if len(events) else np.nan,
        "median_lead_time_min": float(events["lead_time_min"].median()),
        "median_detection_delay_min": float(events["detection_delay_min"].median()),
        "false_alarms_per_well_day": false_alarms_per_well_day(minutes),
        "recall_at_lead": recall_at_lead(events),
        "n_events": int(len(events)),
    }
