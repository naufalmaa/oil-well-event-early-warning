# CLAUDE.md: Oil-Well Event Early Warning

Portfolio project by Naufal MA (data scientist, oil & gas). Part of the `ml-things` traditional-ML roadmap.
Always load the project skill **`ml-portfolio-project`** (in `.claude/skills/`) before working here.

## Facts
- Task: event-detection · Data: 3M DDataset 2.0.0 (Petrobras) (CC BY 4.0)
- Env: WSL2 Ubuntu, Python 3.12, uv. Run everything through `make` / `uv run`.
- Writing language: English for code, docs, notes. Explain hard terms and add them to the glossary in `../ml-research-notes/glossary.md`.

## Hard rules
- Never commit data, model files, `.env`, or anything from clients (PHE OSES, SKK Migas, Proview production data).
- Every result is compared against the baseline and reported with a 95% CI.
- Decide the split (stage 4) before writing features. Leakage tests must pass.
- Parameters live in `configs/`, not in code.

## Mentoring mode
Naufal is learning. When asked to help: explain the *why* briefly, give the next 1–3 concrete steps, and let him write the core modeling code unless he asks otherwise. Point to the source (paper/docs link) for every method.
