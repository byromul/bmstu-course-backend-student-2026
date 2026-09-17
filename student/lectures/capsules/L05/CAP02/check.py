"""Проверка наследования класса и шаблонов."""

from pathlib import Path

from django.conf import settings

root = Path(__file__).parent
templates = {name: (root / name).read_text() for name in ("base.html", "welcome.html")}
settings.configure(
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "OPTIONS": {"loaders": [("django.template.loaders.locmem.Loader", templates)]},
        }
    ]
)
import django

django.setup()
from django.template.loader import get_template
from views import WelcomeView

context = WelcomeView().get_context_data(name="<Ирина>")
html = get_template("welcome.html").render(context)
assert "<body>" in html
assert "&lt;Ирина&gt;" in html
print("CAP02 ПРОЙДЕНА: super(), extends и автоэкранирование работают")
