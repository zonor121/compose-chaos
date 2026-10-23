"""DSL сценария хаоса (v1).

Сценарий описывает: что считать устойчивым состоянием (steady_state),
какие атаки и в каком порядке внедрять (attacks), что наблюдать во время
прогона (monitoring). Схема валидируется Pydantic; JSON Schema для
документации DSL получается методом :meth:`Scenario.to_json_schema`.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class AttackType(str, Enum):
    """Каталог атак. Каждому типу соответствует адаптер из compose_chaos.attacks."""

    # Жизненный цикл контейнеров (Docker API)
    CONTAINER_KILL = "container.kill"
    CONTAINER_PAUSE = "container.pause"
    CONTAINER_STOP = "container.stop"
    # Сетевые деградации (tc netem в sidecar, network_mode: service:target)
    NETEM_DELAY = "netem.delay"
    NETEM_LOSS = "netem.loss"
    NETEM_PARTITION = "netem.partition"  # полная изоляция сервиса
    # Ресурсный стресс (stress-ng в sidecar + docker update по лимитам cgroup)
    STRESS_CPU = "stress.cpu"
    STRESS_MEMORY = "stress.memory"
    STRESS_DISK = "stress.disk"
    # Fallback для сред без CAP_NET_ADMIN/sch_netem (userspace TCP-прокси)
    TOXIPROXY = "toxiproxy.custom"


class ProbeExpect(BaseModel):
    """Ожидаемый ответ пробы."""

    status: int = 200
    body_contains: str | None = None
    max_latency_ms: int | None = None


class ProbeSpec(BaseModel):
    """Спецификация HTTP-пробы (используется и в steady_state, и в monitoring)."""

    name: str
    url: str
    expect: ProbeExpect = Field(default_factory=ProbeExpect)
    interval_sec: float = 5.0


class AttackStep(BaseModel):
    """Один шаг атаки.

    TODO(Этап 2): заменить params: dict на типизированные варианты
    (ContainerParams / NetemParams / StressParams) через pydantic
    discriminated union по полю type.
    """

    name: str
    type: AttackType
    target: str = Field(description="имя сервиса в docker-compose")
    params: dict[str, Any] = Field(default_factory=dict)
    duration_sec: int = Field(default=30, ge=1, description="время воздействия до отката")
    enabled: bool = True


class MonitoringSpec(BaseModel):
    """Что наблюдать во время прогона."""

    stats_interval_sec: float = Field(default=5.0, gt=0)
    probes: list[ProbeSpec] = Field(default_factory=list)


class Scenario(BaseModel):
    """Корневая модель сценария хаоса."""

    schema_version: int = 1
    name: str = Field(min_length=1, max_length=120)
    description: str = ""
    compose_file: Path = Field(description="путь к docker-compose.yml тестируемого приложения")
    steady_state: list[ProbeSpec] = Field(
        default_factory=list,
        description="проверки устойчивого состояния до атаки и после отката",
    )
    attacks: list[AttackStep] = Field(min_length=1)
    monitoring: MonitoringSpec = Field(default_factory=MonitoringSpec)
    rollback_on_breach: bool = Field(
        default=True, description="немедленный откат при нарушении устойчивого состояния"
    )
    total_duration_sec: int | None = Field(
        default=None, ge=1, description="жёсткий лимит длительности прогона"
    )

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Scenario":
        """Загрузка и валидация сценария из YAML-файла."""
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if not isinstance(data, dict):
            raise ValueError("файл сценария должен содержать YAML-отображение (dict)")
        return cls.model_validate(data)

    @classmethod
    def to_json_schema(cls) -> dict[str, Any]:
        """JSON Schema DSL — используется в документации и в редакторах."""
        return cls.model_json_schema()
