"""Запуск всех капсул лекции 5."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for capsule in ("CAP01", "CAP02"):
    result = subprocess.run([sys.executable, "check.py"], cwd=ROOT / capsule, check=False)
    if result.returncode:
        raise SystemExit(result.returncode)
print("КАПСУЛЫ L05 ПРОЙДЕНЫ")
