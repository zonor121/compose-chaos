"""Исполнитель прогона сценария.

План реализации (Этапы 2–3):
1. PREPARE  — ComposeProject.parse(), подъём стенда через DockerGateway,
              проверка steady_state (SteadyStateVerifier, фаза before);
2. ATTACK   — параллельно: адаптеры атак (asyncio.TaskGroup) + StatsCollector
              + HttpProbe-цикл из monitoring;
3. VERIFY   — детекция инцидентов: нарушение проб → incidents (MTTD);
4. ROLLBACK — rollback() каждого адаптера в обратном порядке,
              контроль восстановления (фаза after → MTTR);
5. DONE     — записи в store (runs, attacks, events, metric_samples,
              probe_results, incidents) + генерация отчёта.
"""

from __future__ import annotations

from compose_chaos.models.scenario import Scenario


class RunOrchestrator:
    """Драйвит FSM одного прогона от PREPARE до терминального состояния."""

    def __init__(self, scenario: Scenario) -> None:
        self.scenario = scenario
        # TODO(Этап 2): DockerGateway, StatsCollector, RunRepository (store)

    async def execute(self) -> int:
        """Выполняет прогон, возвращает run_id созданной записи в БД."""
        raise NotImplementedError("реализуется на Этапе 2 (см. docstring модуля)")
