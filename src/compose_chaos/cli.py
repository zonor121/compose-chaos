"""CLI инструмента.

Верхний уровень (argparse, только stdlib) держит `--help` работоспособным
без установленных зависимостей; тяжёлые импорты выполняются лениво внутри
обработчиков команд.
"""

from __future__ import annotations

import argparse
import sys

from compose_chaos import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="compose-chaos",
        description="Хаос-инженерия для локальных docker-compose сред.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="проверить YAML-сценарий по схеме DSL")
    p_validate.add_argument("path", help="путь к файлу сценария")

    p_run = sub.add_parser("run", help="выполнить сценарий (полный цикл FSM)")
    p_run.add_argument("path", help="путь к файлу сценария")
    p_run.add_argument("--dry-run", action="store_true", help="только план атак, без внедрения")

    p_report = sub.add_parser("report", help="сгенерировать отчёт по прогону")
    p_report.add_argument("run_id", type=int, help="идентификатор прогона в БД")
    p_report.add_argument("--format", choices=["html", "json"], default="html")

    p_serve = sub.add_parser("serve", help="запустить веб-интерфейс (FastAPI + uvicorn)")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)

    return parser


def cmd_validate(args: argparse.Namespace) -> int:
    # Ленивый импорт: pydantic/PyYAML нужны только здесь.
    from compose_chaos.models.scenario import Scenario

    try:
        scenario = Scenario.from_yaml(args.path)
    except Exception as exc:  # noqa: BLE001 — CLI-граница, показываем ошибку целиком
        print(f"ОШИБКА: сценарий не прошёл валидацию:\n  {exc}", file=sys.stderr)
        return 1
    print(f"OK: сценарий «{scenario.name}» валиден")
    print(f"    атак: {len(scenario.attacks)}, проб наблюдения: {len(scenario.monitoring.probes)}")
    for step in scenario.attacks:
        print(f"    - [{step.type.value}] {step.name} → {step.target} ({step.duration_sec} c)")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """TODO(Этап 2): собрать зависимости и запустить orchestrator.runner.RunOrchestrator."""
    from compose_chaos.orchestrator.runner import RunOrchestrator  # noqa: F401

    raise NotImplementedError("Оркестратор будет реализован на Этапе 2 (см. README, план этапов)")


def cmd_report(args: argparse.Namespace) -> int:
    """TODO(Этап 4): выгрузить прогон из store и отрендерить через reports."""
    raise NotImplementedError("Отчёты будут реализованы на Этапе 4 (см. README, план этапов)")


def cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    uvicorn.run("compose_chaos.api.app:app", host=args.host, port=args.port, reload=False)
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {
        "validate": cmd_validate,
        "run": cmd_run,
        "report": cmd_report,
        "serve": cmd_serve,
    }
    try:
        code = handlers[args.command](args)
    except NotImplementedError as exc:
        print(f"TODO: {exc}", file=sys.stderr)
        code = 2
    sys.exit(code)


if __name__ == "__main__":
    main()
