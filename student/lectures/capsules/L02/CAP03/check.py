"""Проверка диагностического и успешного запусков Ruff."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(path)],
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="l02-cap03-") as temporary:
        target = Path(temporary) / "example.py"
        shutil.copy2(ROOT / "bad.py", target)
        bad = run(target)
        if bad.returncode == 0 or "F401" not in bad.stdout:
            raise RuntimeError("Ruff не показал F401")
        shutil.copy2(ROOT / "good.py", target)
        good = run(target)
        if good.returncode != 0:
            raise RuntimeError(good.stdout + good.stderr)
    print("[ДИАГНОСТИКА] F401")
    print("[ПОВТОР] All checks passed!")
    print("CAP03 ПРОЙДЕНА")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
