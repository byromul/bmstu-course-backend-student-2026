"""Проверка временной базы и идемпотентного импорта."""

import tempfile
from pathlib import Path

from repository import connect, get_scene, import_scene

with tempfile.TemporaryDirectory(prefix="l04-cap01-") as directory:
    connection = connect(Path(directory) / "game.sqlite3")
    import_scene(connection, {"id": "START", "kind": "choice"})
    import_scene(connection, {"id": "START", "kind": "choice"})
    assert get_scene(connection, "START") == {"id": "START", "kind": "choice"}
    count = connection.execute("SELECT COUNT(*) FROM scenes").fetchone()[0]
    assert count == 1
    connection.close()
print("CAP01 ПРОЙДЕНА: повторный импорт оставил одну сцену START")
