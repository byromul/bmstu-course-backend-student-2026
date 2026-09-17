"""Запустить все капсулы лекции 1 независимо друг от друга."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    for capsule in sorted(ROOT.glob("CAP[0-9][0-9]")):
        completed = subprocess.run(
            [sys.executable, str(capsule / "check.py")],
            cwd=capsule,
            check=False,
        )
        if completed.returncode != 0:
            return completed.returncode
    print("КАПСУЛЫ L01 ПРОЙДЕНЫ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
