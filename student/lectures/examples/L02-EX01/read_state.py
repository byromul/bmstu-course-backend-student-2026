"""Показывает этап разбора JSON без проверки предметного контракта."""

import json
from pathlib import Path

path = Path(__file__).with_name("lecture-state.json")
data = json.loads(path.read_text(encoding="utf-8"))
hp = data["player"]["hp"]
print(f"player.hp: {hp} ({type(hp).__name__})")
