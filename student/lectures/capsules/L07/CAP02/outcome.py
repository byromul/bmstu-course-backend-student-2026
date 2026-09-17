def outcome_for(player, opponent):
    if opponent["hp"] == 0:
        return "player_won"
    if player["hp"] == 0:
        return "player_lost"
    return "continue"
