"""Расчёт одного удара по каноническому контракту D17."""


def resolve_attack(payload):
    player_roll = payload["player_roll"]
    opponent_roll = payload["opponent_roll"]
    if not all(type(value) is int and 1 <= value <= 6 for value in (player_roll, opponent_roll)):
        raise ValueError("бросок должен быть целым числом от 1 до 6")
    player = dict(payload["player"])
    opponent = dict(payload["opponent"])
    player_key = (player_roll, player["str"], player["def"], 1)
    opponent_key = (opponent_roll, opponent["str"], opponent["def"], 0)
    attacker = "player" if player_key >= opponent_key else "opponent"
    attacking, defending = (player, opponent) if attacker == "player" else (opponent, player)
    damage = max(1, attacking["str"] - defending["def"])
    defending["hp"] = max(0, defending["hp"] - damage)
    outcome = "player_won" if opponent["hp"] == 0 else "player_lost" if player["hp"] == 0 else "continue"
    return {"attacker": attacker, "damage": damage, "player": player, "opponent": opponent, "outcome": outcome}
