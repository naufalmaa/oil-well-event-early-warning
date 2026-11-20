"""Stage 2 · Download raw data and verify SHA-256 checksums.

Each file in `configs/default.yaml -> data.files` is either
  - downloaded from `url`, or
  - (when `url` is null) expected to be placed manually in data/raw/ because the
    licence requires registration (e.g. Equinor Volve).
Either way the checksum is verified, so everyone runs on identical bytes.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import requests
from tqdm import tqdm

from ..config import cli_config


def sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def fetch(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        bar = tqdm(total=total, unit="B", unit_scale=True, desc=dest.name)
        with open(dest, "wb") as f, bar:
            for block in r.iter_content(1 << 20):
                f.write(block)
                bar.update(len(block))


def main() -> int:
    cfg = cli_config(__doc__ or "download")
    raw = Path(cfg["paths"]["raw"])
    files = cfg["data"].get("files") or []
    if not files:
        print("No files listed in configs/default.yaml -> data.files. Nothing to do.")
        return 0

    ok = True
    for spec in files:
        dest = raw / spec["name"]
        if not dest.exists():
            if spec.get("url"):
                fetch(spec["url"], dest)
            else:
                print(f"[manual] Place {spec['name']} in {raw}/ (see README > Data).")
                ok = False
                continue
        expected = spec.get("sha256")
        actual = sha256(dest)
        if expected and actual != expected:
            print(f"[FAIL] {dest.name}: sha256 {actual} != expected {expected}")
            ok = False
        elif not expected:
            print(f'[warn] {dest.name}: no checksum pinned yet. Add: sha256: "{actual}"')
        else:
            print(f"[ok]   {dest.name}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
