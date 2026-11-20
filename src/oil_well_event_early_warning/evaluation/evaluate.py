"""Stage 7 · Evaluate every approach against the baseline → reports/metrics.json."""

from __future__ import annotations

from ..config import cli_config


def main() -> None:
    cfg = cli_config(__doc__ or "evaluate")
    raise NotImplementedError(f"Write results to {cfg['paths']['reports']}/metrics.json")


if __name__ == "__main__":
    main()
