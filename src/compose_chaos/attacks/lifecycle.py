"""Атаки на жизненный цикл контейнера через Docker API (kill / pause / stop).

Самый простой класс атак: не требует привилегий, работает в любой среде,
где есть Docker Engine. Восстановление:
- kill  → docker start (дальше действует restart policy сервиса);
- pause → docker unpause;
- stop  → docker start.

TODO(Этап 2): разбор step.params (signal для kill), обработка нескольких
контейнеров одного сервиса, запись фактического времени внедрения.
"""

from __future__ import annotations

from typing import Any

from compose_chaos.attacks.base import AttackAdapter, register
from compose_chaos.models.scenario import AttackStep, AttackType


class LifecycleAttack(AttackAdapter):
    """Базовый адаптер lifecycle-атак; конкретный тип задаётся подклассом."""

    def __init__(self, gateway: Any, step: AttackStep) -> None:
        super().__init__(gateway, step)
        self._affected: list[Any] = []  # контейнеры, затронутые inject()

    async def check_available(self) -> bool:
        # Достаточно, чтобы у целевого сервиса существовал запущенный контейнер.
        raise NotImplementedError("Этап 2")

    async def inject(self) -> None:
        raise NotImplementedError("Этап 2")

    async def rollback(self) -> None:
        raise NotImplementedError("Этап 2")


@register
class KillService(LifecycleAttack):
    """docker kill (SIGKILL по умолчанию) — имитация аварийного падения."""

    type = AttackType.CONTAINER_KILL


@register
class PauseService(LifecycleAttack):
    """docker pause — «зависший» процесс: TCP-соединения висят, ответы нет."""

    type = AttackType.CONTAINER_PAUSE


@register
class StopService(LifecycleAttack):
    """docker stop — корректное завершение, как при плановом рестарте."""

    type = AttackType.CONTAINER_STOP
