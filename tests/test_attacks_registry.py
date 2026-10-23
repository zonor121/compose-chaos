"""Тесты реестра адаптеров атак: каждый тип каталога имеет адаптер."""

from __future__ import annotations

import pytest

from compose_chaos import attacks
from compose_chaos.models.scenario import AttackType

EXPECTED = {
    AttackType.CONTAINER_KILL,
    AttackType.CONTAINER_PAUSE,
    AttackType.CONTAINER_STOP,
    AttackType.NETEM_DELAY,
    AttackType.NETEM_LOSS,
    AttackType.NETEM_PARTITION,
    AttackType.STRESS_CPU,
    AttackType.STRESS_MEMORY,
    AttackType.STRESS_DISK,
    AttackType.TOXIPROXY,
}


def test_all_attack_types_registered() -> None:
    assert set(attacks.available_types()) == EXPECTED


def test_get_adapter_returns_class() -> None:
    adapter_cls = attacks.get_adapter(AttackType.CONTAINER_KILL)
    assert adapter_cls.type is AttackType.CONTAINER_KILL


def test_unknown_type_raises() -> None:
    with pytest.raises(LookupError):
        attacks.get_adapter("no.such.attack")  # type: ignore[arg-type]
