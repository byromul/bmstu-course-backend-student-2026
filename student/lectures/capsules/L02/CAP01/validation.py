"""Проверка снимка до изменения текущего состояния."""

import yaml


def load_state(text: str) -> dict[str, object]:
    data = yaml.safe_load(text)
    if data.get("schema_version") != 1:
        raise ValueError("несовместимая версия")
    player = data.get("player")
    if not isinstance(player, dict) or not isinstance(player.get("hp"), int):
        raise TypeError("hp должен быть целым числом")
    scene_id = data.get("current_scene_id")
    if not isinstance(scene_id, str):
        raise TypeError("current_scene_id должен быть строкой")
    return {"current_scene_id": scene_id, "hp": player["hp"]}
