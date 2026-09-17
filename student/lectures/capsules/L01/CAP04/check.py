"""Воспроизвести красный и зелёный результаты правила выбора."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_tests(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "unittest", "test_choice.py", "-v"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="course-cap04-") as temporary:
        target = Path(temporary)
        shutil.copy2(ROOT / "test_choice.py", target / "test_choice.py")
        shutil.copy2(ROOT / "red" / "choice.py", target / "choice.py")
        red = run_tests(target)
        shutil.copy2(ROOT / "green" / "choice.py", target / "choice.py")
        green = run_tests(target)
    red_ok = red.returncode == 1 and "NotImplementedError" in red.stderr
    green_ok = green.returncode == 0 and "OK" in green.stderr
    if not red_ok or not green_ok:
        print("CAP04 НЕ ПРОЙДЕНА: красно-зелёный переход не воспроизведён", file=sys.stderr)
        return 1
    print("[КРАСНЫЙ] NotImplementedError")
    print("[ЗЕЛЁНЫЙ] Ran 2 tests; OK")
    print("CAP04 ПРОЙДЕНА: NotImplementedError сменился двумя зелёными тестами")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
