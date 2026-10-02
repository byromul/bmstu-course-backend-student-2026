def parse_choice(raw_choice, choices_count):
    try:
        number = int(raw_choice)
    except ValueError:
        raise ValueError("Введите целый номер") from None
    if number not in range(1, choices_count + 1):
        raise ValueError("Такого варианта нет")
    return number - 1


def main():
    choices = ["Крыша", "Метро"]
    for number, text in enumerate(choices, start=1):
        print(f"{number}. {text}")
    selected_index = parse_choice("2", len(choices))
    print(choices[selected_index])


if __name__ == "__main__":
    main()
