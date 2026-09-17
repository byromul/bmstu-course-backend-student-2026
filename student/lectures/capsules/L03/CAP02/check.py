"""Автономная проверка чистого расчёта удара."""

from combat import resolve_attack


def main() -> int:
    player = {"name": "Герой", "hp": 10, "str": 3, "def": 2}
    opponent = {"name": "Крыса", "hp": 4, "str": 2, "def": 1}
    result = resolve_attack(
        {"player": player, "opponent": opponent, "player_roll": 5, "opponent_roll": 2}
    )
    if result != {
        "attacker": "player",
        "damage": 2,
        "player": {"name": "Герой", "hp": 10, "str": 3, "def": 2},
        "opponent": {"name": "Крыса", "hp": 2, "str": 2, "def": 1},
        "outcome": "continue",
    }:
        raise RuntimeError(result)
    if player["hp"] != 10 or opponent["hp"] != 4:
        raise RuntimeError("Исходное состояние изменено")
    tied = resolve_attack(
        {"player": player, "opponent": opponent, "player_roll": 3, "opponent_roll": 3}
    )
    if tied["attacker"] != "player":
        raise RuntimeError("Полное равенство должно разрешаться в пользу игрока")
    print("CAP02 ПРОЙДЕНА: attacker=player, damage=2, исходные состояния сохранены")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
