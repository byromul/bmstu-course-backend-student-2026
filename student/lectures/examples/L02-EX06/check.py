"""Проверка вывода, порога уровня и дополнения UTF-8-файла логов."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(script: Path, directory: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(script)],
        cwd=directory,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )


def main() -> int:
    console_expected = (ROOT / "console.expected.txt").read_text(encoding="utf-8")
    file_expected = (ROOT / "file.expected.txt").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="l02-ex06-") as temporary:
        directory = Path(temporary)
        for name in ("events.py", "console_demo.py", "file_demo.py"):
            shutil.copy2(ROOT / name, directory / name)
        console = run(directory / "console_demo.py", directory)
        if console.stdout or console.stderr != console_expected:
            raise RuntimeError("Вывод в терминал не совпал с ожидаемым")
        if (directory / "game.log").exists():
            raise RuntimeError("Настройка терминала неожиданно создала файл")

        debug_demo = directory / "debug_demo.py"
        debug_demo.write_text(
            (directory / "console_demo.py")
            .read_text(encoding="utf-8")
            .replace("level=logging.INFO", "level=logging.DEBUG"),
            encoding="utf-8",
        )
        debug = run(debug_demo, directory)
        if debug.stdout or debug.stderr != file_expected:
            raise RuntimeError("Изменение порога на DEBUG не показало подробности")

        for count in (1, 2):
            file_run = run(directory / "file_demo.py", directory)
            if file_run.stdout or file_run.stderr:
                raise RuntimeError("При записи в файл сообщения попали в терминал")
            actual = (directory / "game.log").read_text(encoding="utf-8")
            if actual != file_expected * count:
                raise RuntimeError("Файл логов не сохранил записи обоих запусков")
    print("[ТЕРМИНАЛ] INFO и выше; DEBUG скрыт")
    print("[ПОРОГ DEBUG] подробное сообщение появилось")
    print("[ФАЙЛ] UTF-8; записи двух запусков сохранены")
    print("EX06 ПРОЙДЕНА")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
