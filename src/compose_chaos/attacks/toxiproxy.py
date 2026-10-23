"""Toxiproxy — userspace fallback для сетевых атак.

TCP-прокси с динамическими «токсинами» (latency, timeout, bandwidth, сброс
соединений). Не требует CAP_NET_ADMIN и модулей ядра, поэтому работает
в средах, где netem недоступен (rootless Docker, Codespaces).

Компромисс: зависимости сервиса нужно переписать на адрес прокси, т.е.
тестируемая среда изменяется — это отклонение от принципа «не трогать
приложение», поэтому toxiproxy является запасным адаптером, а не основным.

TODO(Этап 2/3): запуск контейнера shopify/toxiproxy, создание прокси и
токсинов через HTTP API (httpx), восстановление исходных адресов после отката.
"""

from __future__ import annotations

from typing import Any

from compose_chaos.attacks.base import AttackAdapter, register
from compose_chaos.models.scenario import AttackStep, AttackType

TOXIPROXY_IMAGE = "shopify/toxiproxy:2.12.0"


@register
class ToxiproxyAttack(AttackAdapter):
    """Универсальный userspace-адаптер (params: toxin, attributes)."""

    type = AttackType.TOXIPROXY

    def __init__(self, gateway: Any, step: AttackStep) -> None:
        super().__init__(gateway, step)
        self._proxy_container_id: str | None = None

    async def check_available(self) -> bool:
        raise NotImplementedError("Этап 3")

    async def inject(self) -> None:
        raise NotImplementedError("Этап 3")

    async def rollback(self) -> None:
        raise NotImplementedError("Этап 3")
