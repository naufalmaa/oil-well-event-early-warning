"""Stage 5 · Baseline.

The simplest thing that could work (threshold rule, persistence, physics curve).
Every later model is reported *relative to this*. If the model can't beat it,
that is a finding, not a failure.
"""

from __future__ import annotations

from ..config import cli_config


def main() -> None:
    cfg = cli_config(__doc__ or "baseline")
    raise NotImplementedError(
        "Implement the baseline for this project, then write its metrics to "
        f"{cfg['paths']['reports']}/metrics.json under key 'baseline'."
    )


if __name__ == "__main__":
    main()
