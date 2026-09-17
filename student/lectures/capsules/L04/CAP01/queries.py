"""Параметризованные запросы учебного репозитория."""


def get_scene(connection, scene_id):
    row = connection.execute(
        "SELECT id, kind FROM scenes WHERE id = ?",
        (scene_id,),
    ).fetchone()
    return dict(row) if row is not None else None
