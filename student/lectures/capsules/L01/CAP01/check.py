"""Проверить CAP01 из нового временного каталога и при необходимости сверить HTML."""

from __future__ import annotations

import argparse
import html
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CAPSULE_ROOT = Path(__file__).resolve().parent
SOURCE = CAPSULE_ROOT / "game_state.py"
EXPECTED = CAPSULE_ROOT / "expected.txt"
SOURCE_REFERENCE = "capsules/L01/CAP01/game_state.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Проверить исполняемую капсулу CAP01")
    parser.add_argument("--html", type=Path, help="Собранная презентация L01 для сверки кода")
    return parser.parse_args()


def check_execution() -> None:
    expected = EXPECTED.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="course-cap01-") as temporary:
        root = Path(temporary)
        shutil.copy2(SOURCE, root / SOURCE.name)
        completed = subprocess.run(
            [sys.executable, SOURCE.name],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    if completed.returncode != 0:
        raise RuntimeError(f"пример завершился с кодом {completed.returncode}: {completed.stderr.strip()}")
    if completed.stderr:
        raise RuntimeError(f"стандартный поток ошибок не пуст: {completed.stderr.strip()}")
    if completed.stdout != expected:
        raise RuntimeError(
            "стандартный вывод не совпал с expected.txt: "
            f"ожидалось {expected!r}, получено {completed.stdout!r}"
        )


def check_html(path: Path) -> None:
    document = path.read_text(encoding="utf-8")
    source = SOURCE.read_text(encoding="utf-8").rstrip("\n")
    source_marker = f'data-code-source-path="{SOURCE_REFERENCE}"'
    code_marker = f"<pre><code>{html.escape(source)}</code></pre>"
    if source_marker not in document:
        raise RuntimeError("в презентации нет ссылки на исходник CAP01")
    if code_marker not in document:
        raise RuntimeError("копируемый код презентации не совпал с game_state.py")


def main() -> int:
    args = parse_args()
    try:
        check_execution()
        if args.html is not None:
            check_html(args.html.resolve())
    except (OSError, RuntimeError, UnicodeError) as error:
        print(f"CAP01 НЕ ПРОЙДЕНА: {error}", file=sys.stderr)
        return 1
    print("CAP01 ПРОЙДЕНА: независимые состояния дают END и START")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
