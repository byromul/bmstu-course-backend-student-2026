"""Проверить сбор и запуск параметризованных тестов в отдельном каталоге."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from importlib.util import find_spec
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    if find_spec("pytest") is None:
        print("Нужен pytest из L02-requirements.lock.", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="l02-ex05-") as temporary:
        target = Path(temporary)
        for name in ("choice.py", "test_choice.py"):
            shutil.copy2(ROOT / name, target / name)
        command = [sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider"]
        collected = subprocess.run(
            [*command, "--collect-only", "test_choice.py"],
            cwd=target,
            capture_output=True,
            text=True,
            check=False,
        )
        if collected.returncode != 0 or collected.stdout.count("test_choice[") != 3:
            raise RuntimeError(collected.stdout + collected.stderr)
        passed = subprocess.run(
            [*command, "test_choice.py"],
            cwd=target,
            capture_output=True,
            text=True,
            check=False,
        )
        if passed.returncode != 0 or "3 passed" not in passed.stdout:
            raise RuntimeError(passed.stdout + passed.stderr)
    print("СОБРАНО: 3 сценария из одной функции")
    print("EX05 ПРОЙДЕНА: 3 passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
