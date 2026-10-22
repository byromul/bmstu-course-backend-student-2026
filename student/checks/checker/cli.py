"""Интерфейс командной строки и формат отчёта ART17."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runner import run_checks
from .spec import get_spec


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _write_report(path: Path, report: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Проверить этап учебного продукта")
    parser.add_argument("--product", required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    product_dir = args.project_dir.resolve()
    report_path = args.report.resolve()
    spec = get_spec(args.product, args.stage)
    if spec is None:
        print("ОШИБКА ВЫЗОВА: продукт и этап несовместимы")
        return 2
    if not product_dir.is_dir():
        print("ОШИБКА ВЫЗОВА: каталог продукта не найден")
        return 2
    if _inside(report_path, product_dir):
        print("ОШИБКА ВЫЗОВА: отчёт должен находиться вне каталога продукта")
        return 2

    checks, mismatch = run_checks(spec, product_dir)
    report: dict[str, object] = {
        "schema_version": 1,
        "product": spec.product,
        "stage": spec.stage,
        "status": "passed" if mismatch is None else "failed",
        "checks": checks,
        "first_mismatch": mismatch,
    }
    try:
        _write_report(report_path, report)
    except OSError as error:
        print(f"ОШИБКА СРЕДЫ: не удалось записать отчёт: {error}")
        return 2
    if mismatch is not None:
        print(f"НЕ ПРОЙДЕНО: {mismatch}")
        return 1
    print(f"ПРОЙДЕНО: {spec.product} {spec.stage}")
    return 0
