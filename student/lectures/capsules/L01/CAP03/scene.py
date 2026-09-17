from dataclasses import dataclass


@dataclass(frozen=True)
class Scene:
    kind = "scene"
    description: str
    choices: tuple[str, ...]

    def is_ending(self):
        return not self.choices
