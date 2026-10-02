from scene import Scene


def announce(function):
    print("Подготовлено отображение")
    return function


@announce
def show(scene):
    print(scene.description)


ending = Scene(description="Вы нашли выход.", choices=())
show(ending)
print(Scene.kind)
print(ending.is_ending())
