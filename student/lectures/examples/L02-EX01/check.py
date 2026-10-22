"""Автономная проверка безопасной загрузки."""

from __future__ import annotations

import shutil
import sys
import tempfile
from importlib.util import find_spec
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    if find_spec("yaml") is None:
        print(
            "Нужен PyYAML: установите зависимости из L02-requirements.lock "
            "в окружение лекции 2.",
            file=sys.stderr,
        )
        return 2
    with tempfile.TemporaryDirectory(prefix="l02-cap01-") as temporary:
        target = Path(temporary)
        shutil.copy2(ROOT / "validation.py", target / "validation.py")
        shutil.copy2(ROOT / "apply_state.py", target / "apply_state.py")
        sys.path.insert(0, str(target))
        from validation import load_state
        from apply_state import load_into

        current = {"current_scene_id": "SCN007", "hp": 6}
        original_id = id(current)
        loaded = load_state(
            "schema_version: 1\ncurrent_scene_id: SCN002\nplayer:\n  hp: 10\n"
        )
        if loaded != {"current_scene_id": "SCN002", "hp": 10}:
            raise RuntimeError("Корректный снимок прочитан неверно")
        failures = (
            ("schema_version: 2\ncurrent_scene_id: SCN002\nplayer:\n  hp: 10\n", ValueError),
            ("[]\n", ValueError),
            ("schema_version: 1\ncurrent_scene_id: SCN002\nplayer:\n  hp: true\n", TypeError),
        )
        for text, expected_error in failures:
            try:
                load_into(current, text)
            except expected_error as error:
                if id(current) != original_id or current != {"current_scene_id": "SCN007", "hp": 6}:
                    raise RuntimeError("Ошибка изменила текущую партию") from error
                if "несовместимая версия" in str(error):
                    print(f"ОТКЛОНЕНО: {error}; ТЕКУЩЕЕ: SCN007, hp=6")
            else:
                raise RuntimeError("Недопустимое сохранение принято")
        load_into(current, "schema_version: 1\ncurrent_scene_id: SCN002\nplayer:\n  hp: 10\n")
        if id(current) != original_id or current != {"current_scene_id": "SCN002", "hp": 10}:
            raise RuntimeError("Проверенное состояние не применено")
    print("EX01 ПРОЙДЕНА")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
