"""Проверка точек расширения DRF."""

from types import SimpleNamespace

from django.conf import settings

settings.configure(INSTALLED_APPS=["django.contrib.auth", "django.contrib.contenttypes"])
import django

django.setup()
from authentication import BearerTokenAuthentication
from permissions import IsScenarioOwner

assert BearerTokenAuthentication().authenticate_header(None) == "Bearer"
permission = IsScenarioOwner()
scene = SimpleNamespace(scenario=SimpleNamespace(owner_id=7))
assert permission.has_object_permission(SimpleNamespace(user=SimpleNamespace(id=7)), None, scene)
assert not permission.has_object_permission(SimpleNamespace(user=SimpleNamespace(id=8)), None, scene)
print("CAP02 ПРОЙДЕНА: Bearer и проверка владельца разделены")
