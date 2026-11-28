"""Stage 4 · Split REAL instances by well.

Every instance of a well goes to the same side. Simulated and drawn
instances never enter the test set (they may be used in training later).
Rare events are spread first so each event type with >= 2 wells reaches test.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def split_wells(
    index: pd.DataFrame, test_size: float = 0.3, seed: int = 42
) -> dict[str, list[str]]:
    real = index[index["source"] == "real"]
    wells_by_event = real.groupby("event")["well_id"].unique()
    rng = np.random.default_rng(seed)
    test: set[str] = set()
    # 1) rare events first: put one of their wells in test if they have >= 2 wells
    for event in wells_by_event.sort_values(key=lambda s: s.map(len)).index:
        wells = sorted(wells_by_event[event])
        if event == 0 or len(wells) < 2 or test.intersection(wells):
            continue
        test.add(str(rng.choice(wells)))
    # 2) fill up to test_size with random remaining wells
    all_wells = sorted(str(w) for w in real["well_id"].unique())
    rest = [w for w in all_wells if w not in test]
    rng.shuffle(rest)
    n_test = max(len(test), round(test_size * len(all_wells)))
    test.update(rest[: n_test - len(test)])
    train = sorted(set(all_wells) - test)
    test = {str(w) for w in test}
    return {"train_wells": train, "test_wells": sorted(test)}


def assign(index: pd.DataFrame, split: dict[str, list[str]]) -> pd.Series:
    """'train' / 'test' / 'sim' per instance."""
    out = pd.Series("sim", index=index.index)
    out[index["well_id"].isin(split["train_wells"])] = "train"
    out[index["well_id"].isin(split["test_wells"])] = "test"
    return out
