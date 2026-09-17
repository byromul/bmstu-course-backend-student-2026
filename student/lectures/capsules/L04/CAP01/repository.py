import sqlite3

from queries import get_scene as _get_scene


def connect(path):
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute(
        "CREATE TABLE IF NOT EXISTS scenes (id TEXT PRIMARY KEY, kind TEXT NOT NULL)"
    )
    return connection


def import_scene(connection, scene):
    connection.execute(
        "INSERT OR REPLACE INTO scenes(id, kind) VALUES (?, ?)",
        (scene["id"], scene["kind"]),
    )
    connection.commit()


def get_scene(connection, scene_id):
    return _get_scene(connection, scene_id)
