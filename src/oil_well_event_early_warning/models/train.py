"""Stage 6 · Train model(s). Log params, metrics and the model to MLflow when installed."""

from __future__ import annotations

from ..config import cli_config


def main() -> None:
    cfg = cli_config(__doc__ or "train")
    raise NotImplementedError(f"Train using split strategy '{cfg['split']['strategy']}'.")


if __name__ == "__main__":
    main()
