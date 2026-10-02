from scene import Scene

ending = Scene(description="Вы нашли выход.", choices=())
same_ending = Scene(description="Вы нашли выход.", choices=())
print(ending)
print(ending == same_ending)
