from copy import deepcopy

from outcome import outcome_for


def resolve_attack(data):
    player = deepcopy(data["player"])
    opponent = deepcopy(data["opponent"])
    player_key = (data["player_roll"], player["str"], player["def"], 1)
    opponent_key = (data["opponent_roll"], opponent["str"], opponent["def"], 0)
    attacker = "player" if player_key >= opponent_key else "opponent"
    attacking, defending = (player, opponent) if attacker == "player" else (opponent, player)
    damage = max(1, attacking["str"] - defending["def"])
    defending["hp"] = max(0, defending["hp"] - damage)
    return {
        "attacker": attacker, "damage": damage,
        "player": player,
        "opponent": opponent,
        "outcome": outcome_for(player, opponent),
    }
