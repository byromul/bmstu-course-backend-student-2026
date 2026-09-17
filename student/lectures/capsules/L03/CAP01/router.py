"""Минимальная маршрутизация учебного API."""

from combat import resolve_attack


def route(method, path, payload):
    if method == "POST" and path == "/api/v1/characters/initialize":
        return 200, {"current_scene_id": "START", "hp": 10}
    if method == "GET" and path == "/api/v1/scenes/START":
        return 200, {"id": "START", "kind": "choice"}
    if method == "POST" and path == "/api/v1/dice/rolls":
        return 200, {"value": 4}
    if method == "POST" and path == "/api/v1/combat/attacks/resolve":
        return 200, resolve_attack(payload)
    return 404, {"error": {"code": "not_found"}}
