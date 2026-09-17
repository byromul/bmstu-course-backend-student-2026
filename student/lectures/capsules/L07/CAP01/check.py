"""Проверка сериализатора DRF."""

from django.conf import settings

settings.configure(USE_I18N=False)
from serializers import AttackSerializer

valid = {
    "player": {"name": "Ирина", "hp": 8, "str": 4, "def": 1},
    "opponent": {"name": "Страж", "hp": 5, "str": 3, "def": 2},
    "player_roll": 6,
    "opponent_roll": 2,
}
serializer = AttackSerializer(data=valid)
assert serializer.is_valid(), serializer.errors
invalid = AttackSerializer(data={**valid, "player_roll": 9})
assert not invalid.is_valid()
assert "player_roll" in invalid.errors
print("CAP01 ПРОЙДЕНА: корректный запрос принят, player_roll=9 отклонён")
