def choice_label(raw_choice, labels):
    number = int(raw_choice)
    if number not in range(1, len(labels) + 1):
        raise ValueError("Такого варианта нет")
    return f"{number}. {labels[number - 1]}"


labels = ["Крыша", "Метро"]
scene_by_id = {"START": {"choices": labels}}
name = "Лина"
hp = 12
ratio = 3 / 2
is_alive = hp > 0
next_scene_id = None

print(name, hp, ratio, is_alive, next_scene_id)
print(choice_label("1", scene_by_id["START"]["choices"]))
print(choice_label(raw_choice="2", labels=labels))
