"""Проверить базовые конструкции Python из нового временного каталога."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_script(source: str, expected_name: str, target_dir: Path) -> bool:
    target = target_dir / source
    shutil.copy2(ROOT / source, target)
    completed = subprocess.run(
        [sys.executable, target.name],
        cwd=target_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    expected = (ROOT / expected_name).read_text(encoding="utf-8")
    return not completed.returncode and not completed.stderr and completed.stdout == expected


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="course-cap02-") as temporary:
        target_dir = Path(temporary)
        basics_ok = run_script("basics.py", "expected.txt", target_dir)
        flow_ok = run_script("control_flow.py", "control_flow.expected.txt", target_dir)
        failures = (
            ("слово", "Введите целый номер"),
            ("0", "Такого варианта нет"),
            ("3", "Такого варианта нет"),
        )
        invalid_ok = True
        for raw_choice, message in failures:
            probe = target_dir / "probe.py"
            probe.write_text(
                "from control_flow import parse_choice\n"
                f"parse_choice({raw_choice!r}, 2)\n",
                encoding="utf-8",
            )
            invalid = subprocess.run(
                [sys.executable, probe.name],
                cwd=target_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            invalid_ok &= invalid.returncode != 0 and f"ValueError: {message}" in invalid.stderr
    if not basics_ok or not flow_ok or not invalid_ok:
        print("EX02 НЕ ПРОЙДЕНА", file=sys.stderr)
        return 1
    print("EX02 ПРОЙДЕНА: значения, коллекции, функции, цикл и проверка ввода воспроизведены")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
