"""Проверка чистого расчёта удара."""

from combat import resolve_attack

data = {
    "player": {"name": "Ирина", "hp": 8, "str": 4, "def": 1},
    "opponent": {"name": "Страж", "hp": 5, "str": 3, "def": 2},
    "player_roll": 6,
    "opponent_roll": 2,
}
result = resolve_attack(data)
assert result["attacker"] == "player"
assert result["damage"] == 2
assert result["opponent"]["hp"] == 3
assert result["outcome"] == "continue"
assert data["opponent"]["hp"] == 5
print("CAP02 ПРОЙДЕНА: атакует player, damage=2, исходные данные не изменены")
