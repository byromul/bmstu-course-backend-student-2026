def choose_next_scene(choices, raw_choice):
    number = int(raw_choice)
    if number not in range(1, len(choices) + 1):
        raise ValueError("Такого варианта нет")
    return choices[number - 1]["next_scene_id"]
