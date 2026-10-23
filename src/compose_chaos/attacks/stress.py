"""Ресурсные атаки: CPU / память / диск.

Два механизма (комбинируются):
1. stress-ng в sidecar с привязкой к ресурсам цели — реальная нагрузка;
2. docker update --cpus / --memory — резкое урезание лимитов cgroup,
   троттлинг возникает под уже идущей нагрузкой.

TODO(Этап 2): разбор step.params (workers, load_percent, duration_sec),
безопасные пределы (не уронить сам хост), откат лимитов через docker update.
"""

from __future__ import annotations

from typing import Any

from compose_chaos.attacks.base import AttackAdapter, register
from compose_chaos.models.scenario import AttackStep, AttackType

STRESS_IMAGE = "polinux/stress-ng:latest"  # TODO: зафиксировать digest


class StressAttack(AttackAdapter):
    def __init__(self, gateway: Any, step: AttackStep) -> None:
        super().__init__(gateway, step)
        self._sidecar_id: str | None = None
        self._prev_limits: dict[str, Any] = {}

    async def check_available(self) -> bool:
        raise NotImplementedError("Этап 2")

    async def inject(self) -> None:
        raise NotImplementedError("Этап 2")

    async def rollback(self) -> None:
        raise NotImplementedError("Этап 2")


@register
class CpuStress(StressAttack):
    """Стресс CPU: stress-ng --cpu N --cpu-load P +/или урезание --cpus."""

    type = AttackType.STRESS_CPU


@register
class MemoryStress(StressAttack):
    """Стресс памяти: vm-воркеры stress-ng; контроль OOM (exit code 137)."""

    type = AttackType.STRESS_MEMORY


@register
class DiskStress(StressAttack):
    """Стресс диска: fill/hdd-воркеры, заполнение тома, IO-нагрузка."""

    type = AttackType.STRESS_DISK
