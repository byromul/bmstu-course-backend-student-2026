"""Проверить EX01 из нового временного каталога и при необходимости сверить HTML."""

from __future__ import annotations

import argparse
import html
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EXERCISE_ROOT = Path(__file__).resolve().parent
SOURCE = EXERCISE_ROOT / "game_state.py"
EXPECTED = EXERCISE_ROOT / "expected.txt"
SOURCE_REFERENCE = "examples/L01-EX01/game_state.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Проверить исполняемую задачу EX01")
    parser.add_argument("--html", type=Path, help="Собранная презентация L01 для сверки кода")
    return parser.parse_args()


def check_execution(source: Path = SOURCE, expected_path: Path = EXPECTED) -> None:
    expected = expected_path.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="course-cap01-") as temporary:
        root = Path(temporary)
        shutil.copy2(source, root / source.name)
        completed = subprocess.run(
            [sys.executable, source.name],
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
            f"стандартный вывод {source.name} не совпал с {expected_path.name}: "
            f"ожидалось {expected!r}, получено {completed.stdout!r}"
        )


def check_html(path: Path) -> None:
    document = path.read_text(encoding="utf-8")
    source = SOURCE.read_text(encoding="utf-8").rstrip("\n")
    source_marker = f'data-code-source-path="{SOURCE_REFERENCE}"'
    code_marker = f"<pre><code>{html.escape(source)}</code></pre>"
    if source_marker not in document:
        raise RuntimeError("в презентации нет ссылки на исходник EX01")
    if code_marker not in document:
        raise RuntimeError("копируемый код презентации не совпал с game_state.py")


def main() -> int:
    args = parse_args()
    try:
        check_execution()
        check_execution(EXERCISE_ROOT / "shared_state.py", EXERCISE_ROOT / "shared.expected.txt")
        if args.html is not None:
            check_html(args.html.resolve())
    except (OSError, RuntimeError, UnicodeError) as error:
        print(f"EX01 НЕ ПРОЙДЕНА: {error}", file=sys.stderr)
        return 1
    print("EX01 ПРОЙДЕНА: независимые состояния дают END и START")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
