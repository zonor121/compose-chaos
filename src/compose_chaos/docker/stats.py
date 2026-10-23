"""Сбор Docker-статистики (CPU/RAM/сеть) во временные ряды.

Источник: GET /containers/{id}/stats?stream=true (стрим JSON-сэмплов).
Пишется в таблицу metric_samples (см. store/models.py) с интервалом
из monitoring.stats_interval_sec.

TODO(Этап 3): вычисление cpu_percent по дельтам cpu_total/system_usage
(как в docker stats), буферизация вставок в БД пачками.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator


@dataclass(slots=True)
class MetricSample:
    """Один сэмпл статистики контейнера."""

    service_name: str
    ts: float
    cpu_percent: float
    mem_usage_mb: float
    mem_limit_mb: float
    net_rx_kbps: float = 0.0
    net_tx_kbps: float = 0.0


@dataclass(slots=True)
class StatsCollector:
    """Фоновая задача сбора статистики на время прогона."""

    gateway: Any
    services: list[str]
    interval_sec: float = 5.0
    _buffer: list[MetricSample] = field(default_factory=list, init=False)

    async def stream(self) -> AsyncIterator[MetricSample]:
        """Стрим сэмплов до отмены задачи."""
        raise NotImplementedError("Этап 3")
        yield  # pragma: no cover — делает функцию асинхронным генератором

    async def flush_to_db(self) -> int:
        """Пакетная вставка буфера в metric_samples; возвращает число строк."""
        raise NotImplementedError("Этап 3")
