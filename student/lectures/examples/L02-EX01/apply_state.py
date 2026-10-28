"""Применить проверенный снимок к текущей партии."""

from validation import load_state


def load_into(current: dict[str, object], text: str) -> None:
    loaded = load_state(text)
    current.update(loaded)
