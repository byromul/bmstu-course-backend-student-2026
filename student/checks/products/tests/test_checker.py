"""Самопроверка внешнего проверяющего средства."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from checker.cli import main
from checker.spec import CONSOLE_HW01


class CheckerInterfaceTests(unittest.TestCase):
    def test_incompatible_product_and_stage_returns_two(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertEqual(
                main(
                    [
                        "--product",
                        "console-quest",
                        "--stage",
                        "HW08",
                        "--project-dir",
                        str(root),
                        "--report",
                        str(root.parent / "unused.json"),
                    ]
                ),
                2,
            )

    def test_missing_files_return_one_and_create_report_outside_product(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "product"
            project.mkdir()
            (project / ".git").mkdir()
            report = root / "reports" / "HW01.json"
            self.assertEqual(
                main(
                    [
                        "--product",
                        "console-quest",
                        "--stage",
                        "HW01",
                        "--project-dir",
                        str(project),
                        "--report",
                        str(report),
                    ]
                ),
                1,
            )
            document = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(document["status"], "failed")
            self.assertEqual(document["checks"][1]["id"], "required-files")
            self.assertNotIn(str(project), report.read_text(encoding="utf-8"))

    def test_hw01_checks_both_endings_and_recovery_in_separate_processes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "console-quest"
            (project / ".git").mkdir(parents=True)
            (project / "client" / "tests").mkdir(parents=True)
            if os.name != "nt":
                (project / ".venv" / "bin").mkdir(parents=True)
                os.symlink(sys.executable, project / ".venv" / "bin" / "python")
            for relative in (
                ".gitignore",
                "README.md",
                "client/__init__.py",
                "client/domain.py",
                "client/tests/__init__.py",
            ):
                (project / relative).write_text("", encoding="utf-8")
            (project / "client" / "tests" / "test_domain.py").write_text(
                """import unittest


class DomainTests(unittest.TestCase):
    def test_fixture_is_ready(self):
        self.assertTrue(True)
""",
                encoding="utf-8",
            )
            (project / "client" / "domain.py").write_text(
                """from dataclasses import dataclass, replace

SCENES = {
    "START": {"kind": "choice", "choices": ({"next_scene_id": "WIN"}, {"next_scene_id": "LOSS"})},
    "WIN": {"kind": "ending", "ending": "positive"},
    "LOSS": {"kind": "ending", "ending": "negative"},
}

@dataclass(frozen=True)
class GameState:
    current_scene_id: str
    name: str
    hp: int
    strength: int
    defense: int

    @classmethod
    def new(cls, name):
        return cls("START", name, 10, 3, 2)

def get_scene(scene_id):
    return SCENES[scene_id]

def choose(state, number):
    if number not in (1, 2):
        raise ValueError("Недопустимый выбор")
    target = SCENES[state.current_scene_id]["choices"][number - 1]["next_scene_id"]
    return replace(state, current_scene_id=target)
""",
                encoding="utf-8",
            )
            (project / "client" / "__main__.py").write_text(
                """name = input()
choice = input()
while choice not in {"1", "2"}:
    print("Вы у развилки.")
    print("1. Светлая")
    print("2. Тёмная")
    print("Ошибка ввода: нужен номер")
    choice = input()
print("Вы у развилки.")
print("1. Светлая")
print("2. Тёмная")
print("Финал: positive" if choice == "1" else "Финал: negative")
""",
                encoding="utf-8",
            )
            report = root / "reports" / "HW01.json"

            self.assertEqual(
                main(
                    [
                        "--product",
                        "console-quest",
                        "--stage",
                        "HW01",
                        "--project-dir",
                        str(project),
                        "--report",
                        str(report),
                    ]
                ),
                0,
            )
            document = json.loads(report.read_text(encoding="utf-8"))
            identifiers = [item["id"] for item in document["checks"]]
            self.assertIn("console-process-positive", identifiers)
            self.assertIn("console-process-negative", identifiers)
            self.assertIn("console-process-recovery", identifiers)

    def test_report_inside_product_returns_two_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            report = project / "report.json"
            self.assertEqual(
                main(
                    [
                        "--product",
                        "console-quest",
                        "--stage",
                        "HW01",
                        "--project-dir",
                        str(project),
                        "--report",
                        str(report),
                    ]
                ),
                2,
            )
            self.assertFalse(report.exists())

    def test_trusted_probe_rejects_empty_domain_and_hardcoded_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "console-quest"
            (project / ".git").mkdir(parents=True)
            for relative in CONSOLE_HW01:
                path = project / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")
            (project / "client" / "__main__.py").write_text(
                'print("1. Готово\\n2. Готово\\nФинал: positive")\n', encoding="utf-8"
            )
            (project / "client" / "tests" / "test_domain.py").write_text(
                "import unittest\n\nclass TrivialTest(unittest.TestCase):\n"
                "    def test_nothing(self):\n        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            report = root / "reports" / "mutant.json"
            self.assertEqual(
                main(
                    [
                        "--product",
                        "console-quest",
                        "--stage",
                        "HW01",
                        "--project-dir",
                        str(project),
                        "--report",
                        str(report),
                    ]
                ),
                1,
            )
            document = json.loads(report.read_text(encoding="utf-8"))
            trusted = next(item for item in document["checks"] if item["id"].startswith("trusted"))
            self.assertEqual(trusted["status"], "failed")


if __name__ == "__main__":
    unittest.main()
