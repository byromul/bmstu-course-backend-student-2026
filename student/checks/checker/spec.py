"""Декларативная спецификация файлов и команд каждого этапа."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StageSpec:
    product: str
    stage: str
    required_paths: tuple[str, ...]
    commands: tuple[tuple[str, ...], ...]


CONSOLE_HW01 = (
    ".gitignore",
    "README.md",
    "client/__init__.py",
    "client/domain.py",
    "client/__main__.py",
)
CONSOLE_HW02 = CONSOLE_HW01 + (
    "requirements.lock",
    "pyproject.toml",
    "schemas/save.schema.json",
    "client/storage.py",
    "client/tests/__init__.py",
    "client/tests/test_domain.py",
    "client/tests/test_storage.py",
)
CONSOLE_HW03 = CONSOLE_HW02 + (
    ".env.example",
    "contracts/openapi.yaml",
    "schemas/scenario.schema.json",
    "client/api.py",
    "client/battle.py",
    "client/tests/test_api.py",
    "client/tests/test_battle.py",
    "client/Dockerfile",
    "server/__init__.py",
    "server/__main__.py",
    "server/http_server.py",
    "server/combat.py",
    "server/data/scenario.yaml",
    "server/tests/__init__.py",
    "server/tests/test_http_api.py",
    "server/tests/test_logging.py",
    "server/tests/test_dice.py",
    "server/tests/test_combat.py",
    "server/Dockerfile",
    "docker-compose.yaml",
)
CONSOLE_HW04 = CONSOLE_HW03 + (
    "server/repository.py",
    "server/import_scenario.py",
    "server/tests/test_repository.py",
    "server/tests/test_import_scenario.py",
)

DJANGO_HW05 = (
    ".gitignore",
    ".env.example",
    "README.md",
    "requirements.lock",
    "pyproject.toml",
    "manage.py",
    "quest/__init__.py",
    "quest/asgi.py",
    "quest/wsgi.py",
    "quest/settings.py",
    "quest/urls.py",
    "game/__init__.py",
    "game/apps.py",
    "game/admin.py",
    "game/models.py",
    "game/views.py",
    "game/migrations/__init__.py",
    "game/urls.py",
    "game/templates/game/base.html",
    "game/templates/game/welcome.html",
    "game/static/game/site.css",
    "game/tests/__init__.py",
    "game/tests/test_views.py",
)
DJANGO_HW06 = DJANGO_HW05 + (
    "data/scenario.yaml",
    "game/scenario_import.py",
    "game/management/__init__.py",
    "game/management/commands/__init__.py",
    "game/management/commands/import_scenario.py",
    "game/migrations/0001_initial.py",
    "game/tests/test_models.py",
    "game/tests/test_import_scenario.py",
)
DJANGO_HW07 = DJANGO_HW06 + (
    "contracts/openapi.yaml",
    "game/serializers.py",
    "game/combat.py",
    "game/api_views.py",
    "game/api_urls.py",
    "game/tests/test_api.py",
    "game/tests/test_combat.py",
)
DJANGO_HW08 = DJANGO_HW07 + (
    "game/authentication.py",
    "game/middleware.py",
    "game/permissions.py",
    "game/migrations/0002_scenario_owner.py",
    "game/tests/test_security.py",
)

UNIT_CLIENT = ("{python}", "-m", "unittest", "discover", "-s", "client/tests", "-v")
UNIT_SERVER = ("{python}", "-m", "unittest", "discover", "-s", "server/tests", "-v")
RUFF = ("{python}", "-m", "ruff", "check", ".")
DJANGO_CHECK = ("{python}", "manage.py", "check")
DJANGO_TEST = ("{python}", "manage.py", "test", "game", "--verbosity", "1")
MIGRATION_CHECK = ("{python}", "manage.py", "makemigrations", "--check", "--dry-run")
OPENAPI_CHECK = ("{python}", "manage.py", "spectacular", "--file", "generated-openapi.yaml", "--validate")

SPECS = {
    ("console-quest", "HW01"): StageSpec(
        "console-quest", "HW01", CONSOLE_HW01, ()
    ),
    ("console-quest", "HW02"): StageSpec(
        "console-quest", "HW02", CONSOLE_HW02, (UNIT_CLIENT, RUFF)
    ),
    ("console-quest", "HW03"): StageSpec(
        "console-quest", "HW03", CONSOLE_HW03, (UNIT_CLIENT, UNIT_SERVER, RUFF)
    ),
    ("console-quest", "HW04"): StageSpec(
        "console-quest", "HW04", CONSOLE_HW04, (UNIT_CLIENT, UNIT_SERVER, RUFF)
    ),
    ("django-quest", "HW05"): StageSpec(
        "django-quest", "HW05", DJANGO_HW05, (DJANGO_CHECK, DJANGO_TEST, RUFF)
    ),
    ("django-quest", "HW06"): StageSpec(
        "django-quest", "HW06", DJANGO_HW06, (DJANGO_CHECK, MIGRATION_CHECK, DJANGO_TEST, RUFF)
    ),
    ("django-quest", "HW07"): StageSpec(
        "django-quest",
        "HW07",
        DJANGO_HW07,
        (DJANGO_CHECK, MIGRATION_CHECK, DJANGO_TEST, OPENAPI_CHECK, RUFF),
    ),
    ("django-quest", "HW08"): StageSpec(
        "django-quest",
        "HW08",
        DJANGO_HW08,
        (DJANGO_CHECK, MIGRATION_CHECK, DJANGO_TEST, OPENAPI_CHECK, RUFF),
    ),
}


def get_spec(product: str, stage: str) -> StageSpec | None:
    return SPECS.get((product, stage))
