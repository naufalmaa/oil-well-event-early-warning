"""Copy figures + case study into the portfolio website repo (porto-naufalma).

Writes, following the website's existing conventions:
  public/asset/projects/<slug>/<figure>.png
  public/asset/article/<slug>-v1.md          (from docs/case-study.md)
Then register it in the DB with the website's seed pattern:
  pnpm tsx src/scripts/seed-<slug>.ts
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

import yaml


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--version", default="v1")
    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    repo = os.environ.get("PORTFOLIO_REPO")
    env = Path(".env")
    if not repo and env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("PORTFOLIO_REPO="):
                repo = line.split("=", 1)[1].strip()
    if not repo or not Path(repo).exists():
        print("Set PORTFOLIO_REPO in .env (see .env.example).")
        return 1

    slug = cfg["publish"]["slug"]
    figs_src = Path(cfg["paths"]["figures"])
    figs_dst = Path(repo) / "public/asset/projects" / slug
    figs_dst.mkdir(parents=True, exist_ok=True)

    missing = []
    for name in cfg["publish"]["figures"]:
        src = figs_src / name
        if src.exists():
            shutil.copy2(src, figs_dst / name)
            print(f"[fig]  {name}")
        else:
            missing.append(name)

    case = Path("docs/case-study.md")
    art_dst = Path(repo) / "public/asset/article" / f"{slug}-{args.version}.md"
    text = case.read_text(encoding="utf-8").replace(
        "](../reports/figures/", f"](/asset/projects/{slug}/"
    )
    art_dst.write_text(text, encoding="utf-8")
    print(f"[md]   {art_dst}")

    if missing:
        print(f"[warn] missing figures: {missing}")
    print(f"Next: in the website repo, run  pnpm tsx src/scripts/seed-{slug}.ts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
