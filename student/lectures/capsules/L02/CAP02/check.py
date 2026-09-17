"""Воспроизведение красного и зелёного этапов AAA-теста."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(target: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "unittest", "-v"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="l02-cap02-") as temporary:
        target = Path(temporary)
        shutil.copy2(ROOT / "test_storage.py", target / "test_storage.py")
        shutil.copy2(ROOT / "red" / "storage.py", target / "storage.py")
        red = run(target)
        if red.returncode == 0 or "NotImplementedError" not in red.stderr:
            raise RuntimeError("Красный этап не достиг NotImplementedError")
        shutil.copy2(ROOT / "green" / "storage.py", target / "storage.py")
        green = run(target)
        if green.returncode != 0 or "Ran 2 tests" not in green.stderr:
            raise RuntimeError(green.stderr)
    print("[КРАСНЫЙ] NotImplementedError")
    print("[ЗЕЛЁНЫЙ] Ran 2 tests; OK")
    print("CAP02 ПРОЙДЕНА")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
