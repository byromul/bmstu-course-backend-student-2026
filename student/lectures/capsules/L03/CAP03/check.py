"""Структурная проверка учебного Compose."""

from pathlib import Path

import yaml


def main() -> int:
    document = yaml.safe_load(Path("compose.yaml").read_text(encoding="utf-8"))
    services = document["services"]
    assert set(services) == {"server", "client"}
    assert services["client"]["environment"]["QUEST_API_URL"] == "http://server:8000"
    assert services["server"]["ports"] == ["127.0.0.1:8000:8000"]
    assert "server-data" in document["volumes"]
    print("CAP03 ПРОЙДЕНА: client → server:8000, порт опубликован на 127.0.0.1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
