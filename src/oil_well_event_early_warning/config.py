"""Load the YAML config and expose a single seeded entry point."""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Any

import numpy as np
import yaml


def load_config(path: str | Path = "configs/default.yaml") -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    seed = cfg.get("seed", 42)
    random.seed(seed)
    np.random.seed(seed)  # noqa: NPY002  (global seed for libraries that use it)
    return cfg


def cli_config(description: str) -> dict[str, Any]:
    """Parse `--config` from the command line and load it."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--config", default="configs/default.yaml")
    args = parser.parse_args()
    return load_config(args.config)
