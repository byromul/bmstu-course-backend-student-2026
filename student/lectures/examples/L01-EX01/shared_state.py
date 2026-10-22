class GameState:
    def __init__(self, current_scene_id):
        self.current_scene_id = current_scene_id


first = GameState("START")
second = first
first.current_scene_id = "END"

print(first.current_scene_id)
print(second.current_scene_id)
