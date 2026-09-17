"""Проверки независимого сценария предварительной подготовки."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "preflight.py"


class PreflightTests(unittest.TestCase):
    def run_preflight(self, *, configured_git: bool) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory(prefix="preflight-test-") as temporary:
            root = Path(temporary)
            git_config = root / "gitconfig"
            if configured_git:
                git_config.write_text(
                    "[user]\n\tname = Тестовый автор\n\temail = author@example.invalid\n",
                    encoding="utf-8",
                )
            else:
                git_config.write_text("", encoding="utf-8")
            environment = os.environ.copy()
            environment.update(
                {
                    "GIT_CONFIG_GLOBAL": str(git_config),
                    "GIT_CONFIG_NOSYSTEM": "1",
                    "PYTHONDONTWRITEBYTECODE": "1",
                }
            )
            return subprocess.run(
                [sys.executable, str(SCRIPT)],
                cwd=root,
                env=environment,
                capture_output=True,
                text=True,
                timeout=180,
                check=False,
            )

    def test_base_profile_uses_temporary_environment_and_repository(self) -> None:
        completed = self.run_preflight(configured_git=True)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("временное окружение и UTF-8", completed.stdout)
        self.assertIn("Git и временный коммит", completed.stdout)
        self.assertIn("ПРЕДВАРИТЕЛЬНАЯ ПРОВЕРКА ПРОЙДЕНА", completed.stdout)
        self.assertNotIn("console-quest", completed.stdout + completed.stderr)

    def test_missing_git_identity_reports_first_recovery_action(self) -> None:
        completed = self.run_preflight(configured_git=False)

        self.assertEqual(completed.returncode, 1)
        self.assertIn("не настроен Git: задайте user.name", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)


if __name__ == "__main__":
    unittest.main()
