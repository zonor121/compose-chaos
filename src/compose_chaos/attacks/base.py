"""Базовый класс адаптера атаки и реестр.

Контракт адаптера:
- check_available() — «доступна ли атака в этой среде» (например, есть ли
  CAP_NET_ADMIN и модуль sch_netem для netem); вызывается оркестратором на
  этапе PREPARE, чтобы сценарий деградировал предсказуемо, а не падал на середине;
- inject()  — внедрение дефекта (идемпотентность на совести адаптера);
- rollback()— гарантированный откат; вызывается даже после частичной аварии.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, TypeVar

from compose_chaos.models.scenario import AttackStep, AttackType

TAdapter = TypeVar("TAdapter", bound="AttackAdapter")

_REGISTRY: dict[AttackType, type["AttackAdapter"]] = {}


def register(cls: type[TAdapter]) -> type[TAdapter]:
    """Декоратор: добавляет класс адаптера в реестр по его AttackType."""
    _REGISTRY[cls.type] = cls
    return cls


def get_adapter(attack_type: AttackType) -> type["AttackAdapter"]:
    try:
        return _REGISTRY[attack_type]
    except KeyError as exc:
        raise LookupError(f"для атаки {attack_type!r} не зарегистрирован адаптер") from exc


def available_types() -> list[AttackType]:
    return sorted(_REGISTRY, key=lambda t: t.value)


class AttackAdapter(ABC):
    """Адаптер одной атаки над целевым compose-стендом."""

    type: ClassVar[AttackType]

    def __init__(self, gateway: Any, step: AttackStep) -> None:
        # gateway: compose_chaos.docker.client.DockerGateway (утиной типизации
        # достаточно до Этапа 2, чтобы избежать циклического импорта)
        self.gateway = gateway
        self.step = step

    @abstractmethod
    async def check_available(self) -> bool:
        """Проверка применимости атаки в текущей среде."""

    @abstractmethod
    async def inject(self) -> None:
        """Внедрить дефект."""

    @abstractmethod
    async def rollback(self) -> None:
        """Откатить дефект, вернуть стенд в исходное состояние."""
