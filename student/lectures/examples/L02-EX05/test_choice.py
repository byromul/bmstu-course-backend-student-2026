"""Одна функция pytest проверяет несколько входных данных."""

import pytest
from choice import choose_scene


@pytest.mark.parametrize(
    "raw, expected",
    [
        pytest.param("1", "WIN", id="first"),
        pytest.param("2", "LOSS", id="second"),
        pytest.param(" 2 ", "LOSS", id="spaces"),
    ],
)
def test_choice(raw: str, expected: str) -> None:
    assert choose_scene(raw) == expected
