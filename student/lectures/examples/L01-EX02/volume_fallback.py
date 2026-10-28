def set_volume(level):
    volume = level or 50  # если не передали — средняя громкость
    return volume


print(set_volume(0))
