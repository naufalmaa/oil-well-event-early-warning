"""`make prepare` · index → split → 1-minute table at data/processed/minutes.parquet."""

from __future__ import annotations

from pathlib import Path

import yaml

from ..config import cli_config
from .load import build_index
from .resample import prepare
from .split import assign


def main() -> None:
    cfg = cli_config(__doc__ or "prepare")
    index = build_index(cfg["data"]["root"])
    with open("configs/split.yaml", encoding="utf-8") as f:
        split = yaml.safe_load(f)
    index["split"] = assign(index, split)
    index = index[index["source"] == "real"]  # sim/drawn: later experiment
    minutes = prepare(index, cfg["features"]["variables"])
    minutes = minutes.merge(index[["instance_id", "split"]], on="instance_id")
    out = Path(cfg["paths"]["processed"]) / "minutes.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    minutes.to_parquet(out, index=False)
    print(f"{len(minutes):,} minutes from {minutes.instance_id.nunique()} instances → {out}")


if __name__ == "__main__":
    main()
