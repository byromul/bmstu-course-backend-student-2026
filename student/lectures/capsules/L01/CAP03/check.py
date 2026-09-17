"""Проверить объектную модель и импорт из нового временного каталога."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_script(name: str, expected_name: str, target: Path) -> bool:
    completed = subprocess.run(
        [sys.executable, name],
        cwd=target,
        capture_output=True,
        text=True,
        check=False,
    )
    expected = (ROOT / expected_name).read_text(encoding="utf-8")
    return not completed.returncode and not completed.stderr and completed.stdout == expected


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="course-cap03-") as temporary:
        target = Path(temporary)
        for name in ("scene.py", "use_scene.py", "frozen_demo.py"):
            shutil.copy2(ROOT / name, target / name)
        object_ok = run_script("use_scene.py", "expected.txt", target)
        frozen_ok = run_script("frozen_demo.py", "frozen.expected.txt", target)
    if not object_ok or not frozen_ok:
        print("CAP03 НЕ ПРОЙДЕНА", file=sys.stderr)
        return 1
    print("CAP03 ПРОЙДЕНА: импорт, dataclass, декоратор, метод и frozen воспроизведены")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
