"""Stage 4 · Leakage tests."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from oil_well_event_early_warning.data.resample import to_minutes

SPLIT = Path("configs/split.yaml")


@pytest.mark.skipif(not SPLIT.exists(), reason="run `make split` first")
def test_no_well_in_both_sides():
    split = yaml.safe_load(SPLIT.read_text())
    assert not set(split["train_wells"]) & set(split["test_wells"])


@pytest.mark.skipif(not SPLIT.exists(), reason="run `make split` first")
def test_only_real_wells_in_test():
    split = yaml.safe_load(SPLIT.read_text())
    assert all(w.startswith("WELL-") for w in split["test_wells"])


def test_minute_features_use_only_past_and_present():
    # a spike in the 2nd minute must not change the 1st minute's features
    idx = pd.date_range("2020-01-01", periods=180, freq="1s")
    base = pd.DataFrame({"P-TPT": np.ones(180), "class": 0}, index=idx)
    spiked = base.copy()
    spiked.iloc[60:120, 0] = 1000.0
    a = to_minutes(base, ["P-TPT"]).iloc[0]
    b = to_minutes(spiked, ["P-TPT"]).iloc[0]
    pd.testing.assert_series_equal(a, b)
