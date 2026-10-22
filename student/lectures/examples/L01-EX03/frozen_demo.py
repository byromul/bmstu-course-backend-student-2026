from dataclasses import FrozenInstanceError

from scene import Scene

ending = Scene(description="Вы нашли выход.", choices=())
try:
    ending.description = "Другое описание"
except FrozenInstanceError as error:
    print(type(error).__name__)
print(ending.description)
