import numpy as np
import pandas as pd

from oil_well_event_early_warning.evaluation.events import apply_alert_rule, summarize


def test_alert_rule_persistence_and_cooldown():
    above = pd.Series([1, 1, 1, 1, 0, 1, 1, 1] + [0] * 60 + [1, 1, 1], dtype=bool)
    alerts = apply_alert_rule(above, persistence=3, cooldown=60)
    assert alerts.sum() == 2  # 2nd burst is inside the cooldown
    assert alerts.iloc[2]  # fires on the 3rd consecutive minute


def _instance(iid, event, labels, alerts, well="W1"):
    n = len(labels)
    return pd.DataFrame(
        {
            "instance_id": iid,
            "well_id": well,
            "event": event,
            "minute": pd.date_range("2020-01-01", periods=n, freq="1min"),
            "label": labels,
            "alert": alerts,
        }
    )


def test_lead_time_and_false_alarms():
    # event 8: normal 10 min, transient (108) 20 min, steady (8) 10 min; alert at minute 15
    lab = [0] * 10 + [108] * 20 + [8] * 10
    al = [False] * 40
    al[15] = True
    ev = _instance("8/WELL-1", 8, lab, al)
    # normal instance: 1 day, 1 alert
    nal = [False] * 1440
    nal[100] = True
    nor = _instance("0/WELL-2", 0, [0] * 1440, nal, well="W2")
    s = summarize(pd.concat([ev, nor], ignore_index=True))
    assert s["event_recall"] == 1.0
    assert s["median_lead_time_min"] == 15  # steady at 30, alert at 15
    assert s["recall_at_lead"][15] == 1.0 and s["recall_at_lead"][30] == 0.0
    assert np.isclose(s["false_alarms_per_well_day"], 1.0)
