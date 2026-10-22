"""Безопасное выполнение проверок во временном зеркале продукта."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from .spec import StageSpec

MAX_OUTPUT = 12_000
SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s]+"),
    re.compile(r"(?i)((?:token|secret(?:_key)?)\s*[=:]\s*)[^\s,;]+"),
)
IGNORED_NAMES = {
    ".git",
    ".venv",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "db.sqlite3",
    "game.sqlite3",
}


def _redact(value: str, replacements: dict[str, str]) -> str:
    safe = value
    for source, replacement in replacements.items():
        safe = safe.replace(source, replacement)
    for pattern in SECRET_PATTERNS:
        safe = pattern.sub(r"\1<СКРЫТО>", safe)
    if len(safe) > MAX_OUTPUT:
        return safe[:MAX_OUTPUT] + "\n<ВЫВОД СОКРАЩЁН>"
    return safe


def _copy_product(source: Path, destination: Path) -> None:
    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in IGNORED_NAMES or name.endswith(".pyc")}

    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if any(part in IGNORED_NAMES for part in relative.parts) or path.name.endswith(".pyc"):
            continue
        if path.is_symlink():
            raise ValueError(f"Символическая ссылка запрещена: {relative}")
    shutil.copytree(source, destination, ignore=ignore)


def _command_result(
    command: tuple[str, ...], workspace: Path, project_root: Path
) -> dict[str, Any]:
    expanded = [sys.executable if item == "{python}" else item for item in command]
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONUTF8": "1",
            "QUEST_DB_PATH": str(workspace / "runtime" / "console.sqlite3"),
            "DJANGO_DB_PATH": str(workspace / "runtime" / "django.sqlite3"),
        }
    )
    (workspace / "runtime").mkdir(exist_ok=True)
    completed = subprocess.run(
        expanded,
        cwd=project_root,
        env=environment,
        text=True,
        capture_output=True,
        timeout=90,
        check=False,
    )
    replacements = {
        str(project_root): "<ЗЕРКАЛО_ПРОДУКТА>",
        str(workspace): "<ВРЕМЕННЫЙ_КАТАЛОГ>",
    }
    return {
        "id": "command:" + " ".join(command),
        "status": "passed" if completed.returncode == 0 else "failed",
        "command": list(command),
        "exit_code": completed.returncode,
        "stdout": _redact(completed.stdout, replacements),
        "stderr": _redact(completed.stderr, replacements),
    }


def _trusted_result(spec: StageSpec, workspace: Path, project_root: Path) -> dict[str, Any]:
    probe = Path(__file__).with_name("trusted_probe.py")
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONUTF8": "1",
            "QUEST_DB_PATH": str(workspace / "runtime" / "trusted-console.sqlite3"),
            "DJANGO_DB_PATH": str(workspace / "runtime" / "trusted-django.sqlite3"),
            "DJANGO_SETTINGS_MODULE": "quest.settings",
        }
    )
    (workspace / "runtime").mkdir(exist_ok=True)
    completed = subprocess.run(
        [sys.executable, str(probe), spec.product, spec.stage],
        cwd=project_root,
        env=environment,
        text=True,
        capture_output=True,
        timeout=90,
        check=False,
    )
    replacements = {
        str(project_root): "<ЗЕРКАЛО_ПРОДУКТА>",
        str(workspace): "<ВРЕМЕННЫЙ_КАТАЛОГ>",
    }
    return {
        "id": f"trusted-behavior:{spec.product}:{spec.stage}",
        "status": "passed" if completed.returncode == 0 else "failed",
        "criteria": ["A01" if spec.product == "console-quest" else "A02", "P"],
        "exit_code": completed.returncode,
        "stdout": _redact(completed.stdout, replacements),
        "stderr": _redact(completed.stderr, replacements),
    }


def _console_process_result(
    identifier: str,
    input_text: str,
    required_fragments: tuple[str, ...],
    workspace: Path,
    project_root: Path,
    *,
    repeated_fragments: tuple[str, ...] = (),
) -> dict[str, Any]:
    environment = os.environ.copy()
    environment.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1"})
    completed = subprocess.run(
        [sys.executable, "-m", "client"],
        cwd=project_root,
        env=environment,
        input=input_text,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    missing = [fragment for fragment in required_fragments if fragment not in completed.stdout]
    for fragment in repeated_fragments:
        if completed.stdout.count(fragment) < 2:
            missing.append(f"повтор фрагмента: {fragment}")
    replacements = {
        str(project_root): "<ЗЕРКАЛО_ПРОДУКТА>",
        str(workspace): "<ВРЕМЕННЫЙ_КАТАЛОГ>",
    }
    passed = completed.returncode == 0 and not completed.stderr and not missing
    return {
        "id": identifier,
        "status": "passed" if passed else "failed",
        "command": ["{python}", "-m", "client"],
        "exit_code": completed.returncode,
        "missing": missing,
        "stdout": _redact(completed.stdout, replacements),
        "stderr": _redact(completed.stderr, replacements),
    }


def run_checks(spec: StageSpec, project_dir: Path) -> tuple[list[dict[str, Any]], str | None]:
    checks: list[dict[str, Any]] = []
    git_exists = (project_dir / ".git").exists()
    checks.append(
        {
            "id": "git-repository",
            "status": "passed" if git_exists else "failed",
        }
    )
    if not git_exists:
        return checks, "Каталог продукта не является Git-репозиторием"
    missing = [path for path in spec.required_paths if not (project_dir / path).is_file()]
    checks.append(
        {
            "id": "required-files",
            "status": "passed" if not missing else "failed",
            "missing": missing,
        }
    )
    if missing:
        return checks, "Отсутствуют обязательные файлы: " + ", ".join(missing)

    with tempfile.TemporaryDirectory(prefix="course-product-check-") as temporary:
        workspace = Path(temporary).resolve()
        mirror = workspace / spec.product
        try:
            _copy_product(project_dir, mirror)
        except (OSError, ValueError) as error:
            checks.append(
                {"id": "read-only-mirror", "status": "failed", "message": str(error)}
            )
            return checks, str(error)
        checks.append({"id": "read-only-mirror", "status": "passed"})
        for command in spec.commands:
            try:
                result = _command_result(command, workspace, mirror)
            except (OSError, subprocess.TimeoutExpired) as error:
                result = {
                    "id": "command:" + " ".join(command),
                    "status": "failed",
                    "command": list(command),
                    "exit_code": None,
                    "stdout": "",
                    "stderr": str(error),
                }
            checks.append(result)
            if result["status"] != "passed":
                return checks, f"Не прошла проверка {result['id']}"
        try:
            trusted = _trusted_result(spec, workspace, mirror)
        except (OSError, subprocess.TimeoutExpired) as error:
            trusted = {
                "id": f"trusted-behavior:{spec.product}:{spec.stage}",
                "status": "failed",
                "exit_code": None,
                "stdout": "",
                "stderr": str(error),
            }
        checks.append(trusted)
        if trusted["status"] != "passed":
            return checks, f"Не прошла проверка {trusted['id']}"
        if spec.product == "console-quest" and spec.stage == "HW01":
            process_checks = (
                _console_process_result(
                    "console-process-positive",
                    "Студент\n1\n",
                    ("1. ", "2. ", "Финал: positive"),
                    workspace,
                    mirror,
                ),
                _console_process_result(
                    "console-process-negative",
                    "Студент\n2\n",
                    ("Финал: negative",),
                    workspace,
                    mirror,
                ),
                _console_process_result(
                    "console-process-recovery",
                    "Студент\nне число\n1\n",
                    ("Ошибка ввода:", "Финал: positive"),
                    workspace,
                    mirror,
                    repeated_fragments=("1. ", "2. "),
                ),
            )
            for result in process_checks:
                checks.append(result)
                if result["status"] != "passed":
                    return checks, f"Не прошла проверка {result['id']}"
    return checks, None
