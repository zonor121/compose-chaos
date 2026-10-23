"""Тесты DSL: пример сценария из scenarios/ обязан валидироваться схемой."""

from __future__ import annotations

from pathlib import Path

from compose_chaos.models.compose import ComposeProject
from compose_chaos.models.scenario import AttackType, Scenario

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "scenarios" / "example_db_kill.yaml"
COMPOSE = ROOT / "demoapp" / "docker-compose.yml"


def test_scenario_yaml_validates() -> None:
    scenario = Scenario.from_yaml(SCENARIO)
    assert scenario.name == "kill-postgres"
    assert scenario.compose_file.name == "docker-compose.yml"


def test_scenario_attack_plan() -> None:
    scenario = Scenario.from_yaml(SCENARIO)
    assert len(scenario.attacks) >= 1
    first = scenario.attacks[0]
    assert first.type is AttackType.CONTAINER_KILL
    assert first.target == "postgres"
    assert first.duration_sec == 30


def test_scenario_json_schema_exportable() -> None:
    schema = Scenario.from_yaml(SCENARIO).to_json_schema()
    assert "attacks" in schema["properties"]


def test_compose_topology_parsed() -> None:
    project = ComposeProject.parse(COMPOSE)
    names = {s.name for s in project.services}
    assert {"nginx", "frontend", "api", "postgres", "redis", "worker"} <= names
    # Направление ребра: зависимость → зависимый (api зависит от postgres).
    assert ("postgres", "api") in project.edges()
    api = next(s for s in project.services if s.name == "api")
    assert api.has_healthcheck
