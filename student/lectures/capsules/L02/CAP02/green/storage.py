def state_from_payload(payload):
    player = payload["player"]
    if not isinstance(player.get("hp"), int):
        raise TypeError("hp должен быть целым числом")
    return payload["current_scene_id"], player["hp"]
