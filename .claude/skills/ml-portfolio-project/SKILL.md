---
name: ml-portfolio-project
description: Conventions, lifecycle stages and the Claude skills to use at each stage for Naufal's traditional-ML portfolio repos in ml-things. Use whenever working in one of these repos, starting a new stage, writing README/model card/case study, or publishing to the portfolio website.
---

# ML portfolio project conventions

## The lifecycle (8 stages + 2 habits)

| # | Stage | Artefact that proves it is done |
|---|---|---|
| 1 | Problem framing & success metrics | `docs/01-problem-framing.md` filled in |
| 2 | Data acquisition & datasheet | `make data` passes checksums; `docs/data-card.md` |
| 3 | EDA & data-quality contract | `notebooks/01-eda.ipynb`; rules in `src/<pkg>/data/schema.py` |
| 4 | Split strategy & leakage audit | `docs/02-split-and-leakage.md`; leakage tests enabled and green |
| 5 | Baseline | `make baseline` writes `metrics.json["baseline"]` |
| 6 | Features & modeling | `make train`; runs tracked (MLflow when installed) |
| 7 | Evaluation, error analysis, tuning, calibration | `make evaluate`; table vs baseline with 95% CI; 3–5 failure cases explained; threshold chosen from cost |
| 8a | Communication | `docs/model-card.md`, README TL;DR filled, `docs/case-study.md` |
| 8b | Deployment, monitoring, retraining | only Project 3 (and the agent API in Project 4) |

Habits: **reproducibility** (seeded, config-driven, one command) and **iteration** (each loop recorded as an ADR in `docs/decisions/`).

## Which Claude skill to use at each stage

| Stage | Skill(s) | Use it for |
|---|---|---|
| 1 | `superpowers:brainstorming`, `mattpocock-skills:grilling` | Sharpen the framing; stress-test assumptions |
| 1, 4 | `mattpocock-skills:research`, `anthropic-skills:deep-research` (sparingly, costly) | Primary-source research saved as Markdown in `docs/research/` |
| 3 | `data:explore-data` | Profile nulls, distributions, duplicates, quality issues |
| 3, 7 | `data:statistical-analysis` | Outliers, tests, correlations, bootstrap |
| 4, 6 | `engineering:testing-strategy`, `superpowers:test-driven-development` | Leakage tests and feature unit tests |
| 6, 8b | `engineering:architecture` | ADRs for design choices |
| 7, 8a | `dataviz`, `data:create-viz` | Every figure in one visual system (`src/<pkg>/viz/style.py`) |
| 7, 8a | `data:validate-data` | QA the analysis before publishing: method, bias, claims supported? |
| 8a | `engineering:documentation` | README, model card, runbook |
| 8b | `engineering:deploy-checklist` | Release checklist for Project 3 |
| any | `superpowers:writing-plans` → `superpowers:executing-plans` | Turn a stage into a step-by-step plan |
| any | `superpowers:verification-before-completion` | Run the commands before claiming done |
| Project 4 | `claude-api` (if Claude is a candidate model) | Model ids, pricing, tool use |
| publishing | `frontend-design` | Only if a new website layout is needed |

## Repo rules

- `ml-things/` is a plain folder. Each subfolder is its own git repo, published as `github.com/naufalmaa/<folder>`.
- New repos come from `ml-things/ml-project-template` via `uvx copier copy --trust`.
- Work inside WSL2 on Ubuntu. Python 3.12 + uv. `make help` lists targets.
- Branch per stage (`stage/03-eda`), conventional commits naming the stage (`feat(baseline): ...`). Tag `v1.0` when the project's "done" list is met.
- Never commit raw data, models, `.env`, or any client material.
- English for everything. Every hard term goes into `ml-research-notes/glossary.md`.

## README rules

Hero image, one-line value proposition, badges, then the **TL;DR table vs baseline with CI**. Then problem, data (source + licence + limits), approach, results, error analysis, "What the model cannot do", reproduce (≤5 commands), structure, decisions, references, citation, author.

## Figures

`viz.style.apply()` first. 1600×900, white background, Okabe–Ito palette, baseline in grey. Save as `NN-name.png` in `reports/figures/`; the number is the website carousel order.

## Publishing to the website (porto-naufalma)

1. Write `docs/case-study.md` (problem → why hard → what I built → results → limits → next).
2. List figures in `configs/default.yaml -> publish.figures`.
3. `make publish-assets` copies figures to `public/asset/projects/<slug>/` and the article to `public/asset/article/<slug>-v1.md`.
4. In the website repo, copy an existing `src/scripts/seed-*.ts` to `seed-<slug>.ts` with tags `["data-ai", "machine-learning"]`, then `pnpm tsx src/scripts/seed-<slug>.ts`.

## Mentoring style (Naufal's preference)

Direct him clearly: short, dense, easy to understand. For each step give: **what** to do, **why** (one sentence + a source link), **how to check it is done**. Let him write the core modeling code; review it afterwards. Quiz him (grilling) at the end of each stage.
