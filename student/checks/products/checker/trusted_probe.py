"""Независимые предметные пробы, не использующие тесты сдаваемого продукта."""

from __future__ import annotations

import copy
import json
import logging
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def console_probe(stage: str) -> None:
    from client.domain import GameState, choose, get_scene

    state = GameState.new("Проверка")
    require(get_scene(state.current_scene_id)["kind"] == "choice", "Нет начальной сцены")
    require(get_scene(choose(state, 1).current_scene_id)["ending"] == "positive", "Нет успеха")
    require(get_scene(choose(state, 2).current_scene_id)["ending"] == "negative", "Нет отказа")
    try:
        choose(state, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("Недопустимый выбор принят")
    if stage == "HW01":
        return

    from client.storage import SaveGameError, load_game, save_game

    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "game.yaml"
        expected = GameState("WIN", "Проверка", 7, 4, 3)
        save_game(path, expected)
        require(load_game(path, lambda item: item == "WIN") == expected, "Состояние не восстановлено")
        try:
            load_game(path, lambda _item: False)
        except SaveGameError:
            pass
        else:
            raise AssertionError("Неизвестная сцена принята")
    if stage == "HW02":
        return

    from server.combat import resolve_attack
    from server.http_server import dispatch

    body = {
        "player": {"name": "Игрок", "hp": 5, "str": 3, "def": 1},
        "opponent": {"name": "Страж", "hp": 4, "str": 2, "def": 2},
        "player_roll": 6,
        "opponent_roll": 1,
    }
    original = copy.deepcopy(body)
    result = resolve_attack(body)
    require(result["attacker"] == "player", "Неверно выбран атакующий")
    require(result["damage"] == 1 and result["opponent"]["hp"] == 3, "Неверный урон")
    require(body == original, "Расчёт изменил запрос")
    damaged = resolve_attack(
        {
            "player": {"name": "Игрок", "hp": 5, "str": 1, "def": 1},
            "opponent": {"name": "Страж", "hp": 5, "str": 3, "def": 1},
            "player_roll": 1,
            "opponent_roll": 6,
        }
    )["player"]
    with tempfile.TemporaryDirectory() as temporary:
        save_path = Path(temporary) / "after-battle.yaml"
        save_game(save_path, GameState("BATTLE", damaged["name"], damaged["hp"], 1, 1))
        code = (
            "from pathlib import Path; from client.storage import load_game; "
            "import sys; print(load_game(Path(sys.argv[1]), lambda value: value == 'BATTLE').hp)"
        )
        restarted = subprocess.run(
            [sys.executable, "-c", code, str(save_path)],
            text=True,
            capture_output=True,
            check=False,
        )
        require(restarted.returncode == 0 and restarted.stdout.strip() == "3", "HP потерян после перезапуска")
    status, payload = dispatch("GET", "/api/v1/dice/rolls")
    require((status, payload["error"]["code"]) == (405, "method_not_allowed"), "Нет 405")
    status, _payload = dispatch("POST", "/api/v1/combat/resolve", body)
    require(status == 404, "Старый путь удара всё ещё принят")
    contract = yaml.safe_load(Path("contracts/openapi.yaml").read_text(encoding="utf-8"))
    operation = contract["paths"]["/api/v1/combat/attacks/resolve"]["post"]
    require(operation["responses"].get("405"), "OpenAPI не описывает 405")
    request_schema = operation["requestBody"]["content"]["application/json"]["schema"]
    require("$ref" in request_schema, "OpenAPI оставляет тело общим object")
    if stage == "HW03":
        return

    from server.import_scenario import import_scenario

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        database = root / "game.sqlite3"
        source = Path("server/data/scenario.yaml")
        import_scenario(source, database)
        with sqlite3.connect(database) as connection:
            connection.execute(
                "INSERT INTO scenario VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("OTHER", "Другой", "OTHER_START", "Иной", 5, 1, 1),
            )
            before = connection.execute("SELECT id FROM scenario ORDER BY id").fetchall()
        document = yaml.safe_load(source.read_text(encoding="utf-8"))
        document["scenes"][0]["choices"][0]["next_scene_id"] = "MISSING"
        broken = root / "broken.yaml"
        broken.write_text(yaml.safe_dump(document, allow_unicode=True), encoding="utf-8")
        try:
            import_scenario(broken, database)
        except ValueError:
            pass
        else:
            raise AssertionError("Повреждённый граф принят")
        with sqlite3.connect(database) as connection:
            after = connection.execute("SELECT id FROM scenario ORDER BY id").fetchall()
        require(after == before, "Неуспешный импорт изменил базу")


def django_probe(stage: str) -> None:
    import django

    django.setup()
    from django.core.management import call_command
    from django.test import Client

    call_command("migrate", verbosity=0, interactive=False)
    client = Client()
    require(client.get("/health/").status_code == 200, "Health-маршрут не работает")
    require(client.get("/welcome/?name=Проверка").status_code == 200, "SSR-маршрут не работает")
    if stage == "HW05":
        return

    from game.models import Scenario, Scene

    require(Scene._meta.pk.name == "id", "Scene.id не является primary key")
    require(not hasattr(Scene, "external_id"), "Сохранён конкурирующий external_id")
    source = Path("data/scenario.yaml")
    if stage in {"HW06", "HW07"}:
        call_command("import_scenario", source=source, verbosity=0)
        require(Scene.objects.count() == 10, "Импортирован неверный минимум сцен")
    if stage == "HW06":
        return

    from game.combat import resolve_attack

    body = {
        "player": {"name": "Игрок", "hp": 5, "str": 3, "def": 1},
        "opponent": {"name": "Страж", "hp": 4, "str": 2, "def": 2},
        "player_roll": 6,
        "opponent_roll": 1,
    }
    require(resolve_attack(body)["opponent"]["hp"] == 3, "Django-удар нарушает контракт")
    contract = yaml.safe_load(Path("contracts/openapi.yaml").read_text(encoding="utf-8"))
    require(len(contract["paths"]) == 4, "В OpenAPI нет четырёх операций")
    generated = yaml.safe_load(Path("generated-openapi.yaml").read_text(encoding="utf-8"))
    expected_statuses = {
        "/api/v1/characters/initialize": {"200", "404", "405"},
        "/api/v1/scenes/{scene_id}": {"200", "404", "405"},
        "/api/v1/dice/rolls": {"200", "405"},
        "/api/v1/combat/attacks/resolve": {"200", "400", "405"},
    }
    if stage == "HW08":
        expected_statuses["/api/v1/characters/initialize"].add("401")
        expected_statuses["/api/v1/scenes/{scene_id}"].update({"401", "403"})
        expected_statuses["/api/v1/dice/rolls"].add("401")
        expected_statuses["/api/v1/combat/attacks/resolve"].add("401")
    for path, statuses in expected_statuses.items():
        operation = next(iter(generated["paths"][path].values()))
        actual = {str(key) for key in operation["responses"]}
        require(statuses <= actual, f"Сгенерированная схема не описывает статусы {path}")
    generated_attack = generated["paths"]["/api/v1/combat/attacks/resolve"]["post"]
    generated_body = generated_attack["requestBody"]["content"]["application/json"]["schema"]
    require("$ref" in generated_body, "Сгенерированная схема оставляет тело общим object")
    if stage == "HW07":
        require(client.post("/api/v1/dice/rolls").status_code == 200, "Бросок недоступен")
        return

    from django.contrib.auth import get_user_model
    from rest_framework.authtoken.models import Token

    Scenario.objects.all().delete()
    users = get_user_model().objects
    owner = users.create_user("trusted-owner")
    other = users.create_user("trusted-other")
    owner_token = Token.objects.create(user=owner)
    other_token = Token.objects.create(user=other)
    call_command("import_scenario", source=source, owner=owner.username, verbosity=0)
    own = Client(HTTP_AUTHORIZATION=f"Bearer {owner_token.key}")
    foreign = Client(HTTP_AUTHORIZATION=f"Bearer {other_token.key}")
    require(client.get("/api/v1/scenes/START").status_code == 401, "Нет 401")
    require(own.get("/api/v1/scenes/START").status_code == 200, "Владелец не допущен")
    require(foreign.get("/api/v1/scenes/START").status_code == 403, "Чужая сцена раскрыта")
    response = own.get("/api/v1/dice/rolls")
    require(response.status_code == 405, "Неверный метод не дал 405")
    require(response.json()["error"]["code"] == "method_not_allowed", "Нестабильный код 405")

    second = Scenario.objects.create(
        id="TRUSTED_OTHER",
        title="Второй ресурс",
        start_scene_id="TRUSTED_START",
        player_name="Другой",
        player_hp=5,
        player_str=1,
        player_def=1,
        owner=other,
    )
    Scene.objects.create(
        id="TRUSTED_START",
        scenario=second,
        description="Другой старт",
        kind="ending",
    )
    require(foreign.get("/api/v1/scenes/TRUSTED_START").status_code == 200, "Второй владелец не допущен")
    require(own.get("/api/v1/scenes/TRUSTED_START").status_code == 403, "Перенос владения не работает")

    class Capture(logging.Handler):
        def __init__(self) -> None:
            super().__init__()
            self.messages: list[str] = []

        def emit(self, record: logging.LogRecord) -> None:
            self.messages.append(record.getMessage())

    capture = Capture()
    logger = logging.getLogger("quest.requests")
    logger.addHandler(capture)
    logger.setLevel(logging.INFO)
    try:
        own.get("/api/v1/scenes/START")
    finally:
        logger.removeHandler(capture)
    joined = "\n".join(capture.messages)
    require(owner_token.key not in joined, "Токен попал в журнал")
    record = json.loads(capture.messages[-1])
    required = {"request_id", "method", "path", "status", "duration_ms", "reason_code"}
    require(required <= set(record), "В журнале нет обязательных полей")


def main() -> int:
    product, stage = sys.argv[1:3]
    sys.path.insert(0, str(Path.cwd()))
    if product == "console-quest":
        console_probe(stage)
    else:
        django_probe(stage)
    print(f"ДОВЕРЕННАЯ ПРОБА ПРОЙДЕНА: {product} {stage}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
