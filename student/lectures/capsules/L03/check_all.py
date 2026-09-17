"""Запуск всех капсул лекции 3."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    for capsule in ("CAP01", "CAP02", "CAP03"):
        completed = subprocess.run(
            [sys.executable, "check.py"], cwd=ROOT / capsule, check=False
        )
        if completed.returncode != 0:
            return completed.returncode
    print("КАПСУЛЫ L03 ПРОЙДЕНЫ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
