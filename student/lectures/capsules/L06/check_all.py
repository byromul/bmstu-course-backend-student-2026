"""Запуск всех капсул лекции 6."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
result = subprocess.run([sys.executable, "check.py"], cwd=ROOT / "CAP01", check=False)
if result.returncode:
    raise SystemExit(result.returncode)
print("КАПСУЛЫ L06 ПРОЙДЕНЫ")
