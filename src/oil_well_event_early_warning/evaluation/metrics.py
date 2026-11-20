"""Stage 7 · Metrics with uncertainty.

`bootstrap_ci` resamples *groups* (wells, machines, events) rather than rows when
`groups` is given, because rows inside one asset are not independent.
Reference: Raschka (2018), https://arxiv.org/abs/1811.12808
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np


def bootstrap_ci(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    metric: Callable[[np.ndarray, np.ndarray], float],
    *,
    groups: np.ndarray | None = None,
    n_resamples: int = 1000,
    ci: float = 0.95,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Return (point_estimate, lower, upper)."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    rng = np.random.default_rng(seed)
    point = float(metric(y_true, y_pred))

    if groups is None:
        units = np.arange(len(y_true))
        index_of = {u: np.array([u]) for u in units}
    else:
        groups = np.asarray(groups)
        units = np.unique(groups)
        index_of = {u: np.flatnonzero(groups == u) for u in units}

    stats = []
    for _ in range(n_resamples):
        sample = rng.choice(units, size=len(units), replace=True)
        idx = np.concatenate([index_of[u] for u in sample])
        try:
            stats.append(metric(y_true[idx], y_pred[idx]))
        except ValueError:  # e.g. a resample with a single class
            continue
    alpha = (1 - ci) / 2
    lo, hi = np.quantile(stats, [alpha, 1 - alpha])
    return point, float(lo), float(hi)


def mase(y_true: np.ndarray, y_pred: np.ndarray, y_train: np.ndarray, m: int = 1) -> float:
    """Mean Absolute Scaled Error (Hyndman & Koehler, 2006).

    Scales MAE by the in-sample MAE of the naive (lag-m) forecast, so it stays
    finite when actuals are zero (shut-in days), unlike MAPE.
    """
    y_train = np.asarray(y_train, dtype=float)
    scale = np.mean(np.abs(y_train[m:] - y_train[:-m]))
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))) / scale)
