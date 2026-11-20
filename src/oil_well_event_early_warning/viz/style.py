"""One visual system for every figure in the portfolio.

Call `apply()` once at the top of a notebook/script. Figures are saved at
1600x900 (16:9) so they drop straight into the website carousel.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

# Categorical palette (colour-blind safe, Okabe–Ito based). Swap here only.
PALETTE = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#000000"]
BASELINE_GREY = "#9AA0A6"
FIGSIZE = (16, 9)
DPI = 100  # 16x9 in * 100 dpi = 1600x900 px


def apply() -> None:
    mpl.rcParams.update(
        {
            "figure.figsize": FIGSIZE,
            "figure.dpi": DPI,
            "axes.prop_cycle": mpl.cycler(color=PALETTE),
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "axes.titlesize": 20,
            "axes.titleweight": "bold",
            "axes.labelsize": 15,
            "xtick.labelsize": 13,
            "ytick.labelsize": 13,
            "legend.fontsize": 13,
            "legend.frameon": False,
            "font.family": "DejaVu Sans",
        }
    )


def save(fig: plt.Figure, name: str, figures_dir: str | Path = "reports/figures") -> Path:
    """Save as NN-name.png (the number sets the website carousel order)."""
    out = Path(figures_dir) / name
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor="white")
    return out
