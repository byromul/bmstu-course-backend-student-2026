"""Проверка матрицы безопасности."""

from security import authenticate, read_scene

scene = {"id": "START", "owner": "anton"}
assert authenticate("") is None
assert authenticate("Bearer") is None
assert authenticate("Bearer damaged") is None
assert read_scene("", scene, {"START"}) == 401
assert read_scene("Bearer opaque-irina", scene, {"START"}) == 403
assert read_scene("Bearer opaque-irina", scene, set()) == 404
assert read_scene("Bearer opaque-anton", scene, set()) == 404
assert read_scene("Bearer opaque-anton", scene, {"START"}) == 200
print("CAP01 ПРОЙДЕНА: 401, 403, 404 и 200 различаются")
