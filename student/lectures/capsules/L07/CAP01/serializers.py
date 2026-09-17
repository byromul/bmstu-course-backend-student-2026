from rest_framework import serializers


class ParticipantSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    hp = serializers.IntegerField(min_value=1)
    str = serializers.IntegerField(min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["def"] = serializers.IntegerField(min_value=0)


class AttackSerializer(serializers.Serializer):
    player_roll = serializers.IntegerField(min_value=1, max_value=6)
    opponent_roll = serializers.IntegerField(min_value=1, max_value=6)
    player = ParticipantSerializer()
    opponent = ParticipantSerializer()
