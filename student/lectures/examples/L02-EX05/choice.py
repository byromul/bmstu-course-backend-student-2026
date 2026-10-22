"""Небольшое правило выбора сцены для параметризованного теста."""


def choose_scene(raw: str) -> str:
    number = int(raw)
    if number not in (1, 2):
        raise ValueError("Такого варианта нет")
    return ("WIN", "LOSS")[number - 1]
