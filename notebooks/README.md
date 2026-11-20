# Notebooks

Narrative only. Reusable logic belongs in `src/`, and notebooks import from it.

| Notebook | Stage | Question it answers |
|---|---|---|
| `01-eda.ipynb` | 3 | What is in the data, and what is wrong with it? → rules in `schema.py` |
| `02-baseline.ipynb` | 5 | How good is the simplest approach? |
| `03-error-analysis.ipynb` | 7 | Where and why does the model fail? |

Outputs are stripped on commit (nbstripout). Figures for the README are saved by code to `reports/figures/`.
