"""HTTP-проба: код ответа, тело, латентность.

Проверки (см. ProbeSpec.expect в DSL):
- status — ожидаемый HTTP-код;
- body_contains — подстрока/регулярное выражение в теле;
- max_latency_ms — верхняя граница латентности.

Пробо-цикл мониторинга пишет результаты в probe_results; вердикты
устойчивого состояния — в steady_state_checks.

TODO(Этап 3): реализовать check() на httpx.AsyncClient; вынести
сопоставление с expect в чистую функцию (легко тестировать).
"""

from __future__ import annotations

from dataclasses import dataclass

from compose_chaos.models.scenario import ProbeSpec


@dataclass(slots=True)
class ProbeOutcome:
    """Результат одной пробы."""

    ok: bool
    status_code: int | None
    latency_ms: float
    error: str | None = None


class HttpProbe:
    def __init__(self, spec: ProbeSpec, timeout_sec: float = 5.0) -> None:
        self.spec = spec
        self.timeout_sec = timeout_sec

    async def check(self) -> ProbeOutcome:
        raise NotImplementedError("Этап 3")
