"""Проверка минимального маршрута Django."""

import app  # noqa: F401
from django.test import Client
from django.urls import reverse

response = Client().get(reverse("health"))
assert response.status_code == 200
assert response.json() == {"status": "ok"}
print("CAP01 ПРОЙДЕНА: GET /health/ → 200 {'status': 'ok'}")
