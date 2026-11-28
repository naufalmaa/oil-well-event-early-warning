"""`make split` · write configs/split.yaml once (then commit it; never regenerate silently)."""

from __future__ import annotations

import yaml

from ..config import cli_config
from .load import build_index
from .split import split_wells


def main() -> None:
    cfg = cli_config(__doc__ or "split")
    index = build_index(cfg["data"]["root"])
    split = split_wells(index, cfg["split"]["test_size"], cfg["seed"])
    with open("configs/split.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(split, f)
    real = index[index.source == "real"].assign(
        side=lambda d: d.well_id.isin(split["test_wells"]).map({True: "test", False: "train"})
    )
    print(
        real.pivot_table(
            index="event", columns="side", values="path", aggfunc="count", fill_value=0
        )
    )


if __name__ == "__main__":
    main()
