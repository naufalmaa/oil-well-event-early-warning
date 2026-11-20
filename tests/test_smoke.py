import numpy as np
from sklearn.metrics import mean_absolute_error

from oil_well_event_early_warning.config import load_config
from oil_well_event_early_warning.evaluation.metrics import bootstrap_ci, mase


def test_config_loads():
    cfg = load_config("configs/default.yaml")
    assert "paths" in cfg and "split" in cfg


def test_bootstrap_ci_brackets_point_estimate():
    rng = np.random.default_rng(0)
    y = rng.normal(size=200)
    p = y + rng.normal(scale=0.5, size=200)
    point, lo, hi = bootstrap_ci(y, p, mean_absolute_error, n_resamples=200)
    assert lo <= point <= hi


def test_bootstrap_ci_by_group():
    rng = np.random.default_rng(1)
    y = rng.normal(size=300)
    p = y + rng.normal(scale=0.3, size=300)
    groups = np.repeat(np.arange(10), 30)
    point, lo, hi = bootstrap_ci(y, p, mean_absolute_error, groups=groups, n_resamples=200)
    assert lo <= point <= hi


def test_mase_is_finite_with_zero_actuals():
    y_train = np.array([10, 9, 0, 8, 7, 0, 6], dtype=float)
    assert np.isfinite(mase(np.zeros(3), np.ones(3), y_train))
