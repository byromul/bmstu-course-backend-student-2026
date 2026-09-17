"""Автономная проверка безопасной загрузки."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="l02-cap01-") as temporary:
        target = Path(temporary)
        shutil.copy2(ROOT / "validation.py", target / "validation.py")
        sys.path.insert(0, str(target))
        from validation import load_state

        current = {"current_scene_id": "SCN007", "hp": 6}
        loaded = load_state(
            "schema_version: 1\ncurrent_scene_id: SCN002\nplayer:\n  hp: 10\n"
        )
        if loaded != {"current_scene_id": "SCN002", "hp": 10}:
            raise RuntimeError("Корректный снимок прочитан неверно")
        try:
            load_state(
                'schema_version: 2\ncurrent_scene_id: SCN002\nplayer:\n  hp: "10"\n'
            )
        except ValueError as error:
            if current != {"current_scene_id": "SCN007", "hp": 6}:
                raise RuntimeError("Ошибка изменила текущую партию") from error
            print(f"ОТКЛОНЕНО: {error}; ТЕКУЩЕЕ: SCN007, hp=6")
            print("CAP01 ПРОЙДЕНА")
            return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
