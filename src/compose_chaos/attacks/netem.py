"""Сетевые деградации через tc netem в sidecar-контейнере.

Механика: sidecar запускается с network_mode: service:<target> и CAP_NET_ADMIN,
внутри него `tc qdisc add dev eth0 root netem ...` меняет qdisc сетевого
интерфейса, который разделяет целевой контейнер. Целевой образ не меняется,
откат — `tc qdisc del dev eth0 root` (или удаление sidecar).

Ограничения среды: нужен CAP_NET_ADMIN и загруженный модуль ядра sch_netem.
check_available() обязан проверять оба условия — отсюда же fallback на
toxiproxy (см. toxiproxy.py) для сред без привилегий (например, Codespaces).

TODO(Этап 2): шаблон sidecar-контейнера (docker SDK create_container),
выбор интерфейса, разграничение delay/loss/partition.
"""

from __future__ import annotations

from typing import Any

from compose_chaos.attacks.base import AttackAdapter, register
from compose_chaos.models.scenario import AttackStep, AttackType

SIDECAR_IMAGE = "ghcr.io/chaosplanet/netem-sidecar:latest"  # TODO: собрать свой образ


class NetemAttack(AttackAdapter):
    """Общая логика netem-атак; конкретный дефект задаётся подклассом."""

    def __init__(self, gateway: Any, step: AttackStep) -> None:
        super().__init__(gateway, step)
        self._sidecar_id: str | None = None

    async def check_available(self) -> bool:
        # 1) docker run --rm --cap-add NET_ADMIN <image> tc qdisc add ... netem
        # 2) при ошибке «Unknown qdisc» — модуль sch_netem недоступен → False
        raise NotImplementedError("Этап 2")

    async def inject(self) -> None:
        raise NotImplementedError("Этап 2")

    async def rollback(self) -> None:
        raise NotImplementedError("Этап 2")


@register
class DelayService(NetemAttack):
    """Добавленная задержка ± джиттер (params: delay_ms, jitter_ms)."""

    type = AttackType.NETEM_DELAY


@register
class LossService(NetemAttack):
    """Потери пакетов в процентах (params: loss_percent)."""

    type = AttackType.NETEM_LOSS


@register
class PartitionService(NetemAttack):
    """Полная сетевая изоляция сервиса (iptables DROP внутри netns)."""

    type = AttackType.NETEM_PARTITION
