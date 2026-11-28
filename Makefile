# Run inside WSL2. Every target is reproducible from a clean clone.
.DEFAULT_GOAL := help
PKG := oil_well_event_early_warning
RUN := uv run

.PHONY: help setup data split prepare eda baseline train evaluate test lint format publish-assets clean

help: ## List targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

setup: ## Install deps (uv) and git hooks
	uv sync --all-extras
	$(RUN) pre-commit install
	$(RUN) nbstripout --install

data: ## Stage 2 · download raw data and verify checksums
	$(RUN) python -m $(PKG).data.download --config configs/default.yaml

split: ## Stage 4 · write configs/split.yaml (run once, then commit it)
	$(RUN) python -m $(PKG).data.make_split --config configs/default.yaml

prepare: ## Stage 3→6 · 1 Hz instances → data/processed/minutes.parquet
	$(RUN) python -m $(PKG).data.prepare --config configs/default.yaml

baseline: ## Stage 5 · run the baseline and write its metrics
	$(RUN) python -m $(PKG).models.baseline --config configs/default.yaml

train: ## Stage 6 · train the model(s)
	$(RUN) python -m $(PKG).models.train --config configs/default.yaml

evaluate: ## Stage 7 · evaluate vs baseline → reports/metrics.json + figures
	$(RUN) python -m $(PKG).evaluation.evaluate --config configs/default.yaml

test: ## Unit + leakage tests
	$(RUN) pytest

lint: ## Ruff lint + format check
	$(RUN) ruff check .
	$(RUN) ruff format --check .

format: ## Auto-format
	$(RUN) ruff check --fix .
	$(RUN) ruff format .

publish-assets: ## Copy figures + case study into the portfolio website repo
	$(RUN) python scripts/publish_assets.py --config configs/default.yaml

clean: ## Remove generated data and models (keeps raw data)
	rm -rf data/interim/* data/processed/* models/*
