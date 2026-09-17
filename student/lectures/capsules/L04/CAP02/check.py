"""Структурная проверка учебного OpenAPI."""

from pathlib import Path

import yaml

document = yaml.safe_load(Path("openapi.yaml").read_text(encoding="utf-8"))
assert document["openapi"] == "3.1.0"
expected = {
    ("/api/v1/characters/initialize", "post"),
    ("/api/v1/scenes/{scene_id}", "get"),
    ("/api/v1/dice/rolls", "post"),
    ("/api/v1/combat/attacks/resolve", "post"),
}
actual = {(path, method) for path, item in document["paths"].items() for method in item}
assert actual == expected
print("CAP02 ПРОЙДЕНА: OpenAPI 3.1 описывает четыре операции")
