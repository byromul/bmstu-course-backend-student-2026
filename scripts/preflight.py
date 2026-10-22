"""Проверить базовую среду курса без готового учебного продукта."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PYTHON_VERSION = (3, 14, 7)
CONTAINER_IMAGE = "docker.io/library/python:3.14.7-slim"


class CheckFailed(RuntimeError):
    """Ожидаемое несоответствие среды."""


def run_command(
    command: list[str],
    *,
    cwd: Path,
    timeout: int = 120,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise CheckFailed(f"не удалось выполнить {' '.join(command)}: {error}") from error


def require_success(
    command: list[str],
    *,
    cwd: Path,
    timeout: int = 120,
) -> subprocess.CompletedProcess[str]:
    completed = run_command(command, cwd=cwd, timeout=timeout)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        suffix = f": {detail}" if detail else ""
        raise CheckFailed(
            f"команда {' '.join(command)} завершилась с кодом {completed.returncode}{suffix}"
        )
    return completed


def check_python() -> None:
    if sys.version_info[:3] != PYTHON_VERSION:
        expected = ".".join(str(part) for part in PYTHON_VERSION)
        raise CheckFailed(f"нужен Python {expected}, получен {sys.version.split()[0]}")
    print(f"[ПРОЙДЕНО] Python {sys.version.split()[0]}")


def environment_python(environment: Path) -> Path:
    if sys.platform == "win32":
        return environment / "Scripts" / "python.exe"
    return environment / "bin" / "python"


def check_temporary_environment(root: Path) -> None:
    environment = root / "environment"
    require_success([sys.executable, "-m", "venv", str(environment)], cwd=root)
    python = environment_python(environment)
    probe = (
        "from pathlib import Path; "
        "path = Path('utf8-probe.txt'); "
        "path.write_text('Квест готов\\n', encoding='utf-8'); "
        "print(path.read_text(encoding='utf-8'), end='')"
    )
    completed = require_success([str(python), "-c", probe], cwd=root)
    if completed.stdout != "Квест готов\n" or completed.stderr:
        raise CheckFailed("временное окружение не воспроизвело запись и чтение UTF-8")
    print("[ПРОЙДЕНО] временное окружение и UTF-8")


def read_git_config(key: str, root: Path) -> str:
    completed = run_command(["git", "config", "--get", key], cwd=root)
    if completed.returncode != 0 or not completed.stdout.strip():
        raise CheckFailed(f"не настроен Git: задайте {key}")
    return completed.stdout.strip()


def check_git(root: Path) -> None:
    if shutil.which("git") is None:
        raise CheckFailed("Git не найден в PATH")
    require_success(["git", "--version"], cwd=root)
    read_git_config("user.name", root)
    read_git_config("user.email", root)
    repository = root / "repository"
    repository.mkdir()
    require_success(["git", "init", "-b", "main"], cwd=repository)
    (repository / "README.md").write_text(
        "# Пробный репозиторий\n\nФайл создан предварительной проверкой.\n",
        encoding="utf-8",
    )
    require_success(["git", "add", "README.md"], cwd=repository)
    require_success(["git", "commit", "-m", "Проверить локальный Git"], cwd=repository)
    status = require_success(["git", "status", "--porcelain"], cwd=repository)
    if status.stdout:
        raise CheckFailed("временный Git-репозиторий остался с незаписанными изменениями")
    print("[ПРОЙДЕНО] Git и временный коммит")


def available_container_engine(root: Path) -> str:
    diagnostics: list[str] = []
    for engine in ("podman", "docker"):
        if shutil.which(engine) is None:
            continue
        completed = run_command([engine, "version"], cwd=root)
        if completed.returncode == 0:
            return engine
        detail = (completed.stderr or completed.stdout).strip()
        diagnostics.append(f"{engine}: {detail or f'код {completed.returncode}'}")
    if diagnostics:
        raise CheckFailed("система контейнеризации не готова: " + "; ".join(diagnostics))
    raise CheckFailed("не найдены Podman или Docker")


def check_containers(root: Path) -> str:
    engine = available_container_engine(root)
    image = run_command([engine, "image", "inspect", CONTAINER_IMAGE], cwd=root)
    if image.returncode != 0:
        raise CheckFailed(
            f"образ {CONTAINER_IMAGE} не загружен; выполните {engine} pull {CONTAINER_IMAGE} и повторите проверку"
        )
    completed = require_success(
        [engine, "run", "--rm", CONTAINER_IMAGE, "python", "--version"],
        cwd=root,
    )
    output = (completed.stdout or completed.stderr).strip()
    if output != "Python 3.14.7":
        raise CheckFailed(f"{engine} запустил неожиданную версию: {output}")
    print(f"[ПРОЙДЕНО] контейнерный запуск через {engine}")
    return engine


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Проверить готовность учебной среды")
    parser.add_argument(
        "--profile",
        choices=("base", "containers"),
        default="base",
        help="base — подготовка к первой лекции; containers — дополнительная проверка к лекции 3",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        check_python()
        with tempfile.TemporaryDirectory(prefix="course-preflight-") as temporary:
            root = Path(temporary)
            check_temporary_environment(root)
            check_git(root)
            engine = check_containers(root) if args.profile == "containers" else None
    except CheckFailed as error:
        print(f"ПРОВЕРКА НЕ ПРОЙДЕНА: {error}", file=sys.stderr)
        return 1
    detail = f", контейнерный запуск через {engine}" if engine else ""
    print(
        "ПРЕДВАРИТЕЛЬНАЯ ПРОВЕРКА ПРОЙДЕНА: "
        f"Python {sys.version.split()[0]}, временное окружение, UTF-8 и Git{detail}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
