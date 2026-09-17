"""Проверка отношений и ограничения моделей."""

from django.conf import settings

settings.configure(
    INSTALLED_APPS=[],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    SECRET_KEY="lecture-only",
)
import django

django.setup()
from django.db import IntegrityError, connection, transaction
from models import Scenario, Scene

with connection.schema_editor() as editor:
    editor.create_model(Scenario)
    editor.create_model(Scene)
scenario = Scenario.objects.create(title="Путь")
Scene.objects.create(id="START", scenario=scenario, kind="choice")
other = Scenario.objects.create(title="Другой путь")
try:
    with transaction.atomic():
        Scene.objects.create(id="START", scenario=other, kind="ending")
except IntegrityError:
    pass
else:
    raise AssertionError("первичный ключ сцены не сработал")
assert Scene._meta.pk.name == "id"
assert Scene.objects.get(pk="START").scenario_id == scenario.id
print("CAP01 ПРОЙДЕНА: строковый Scene.id — первичный ключ")
