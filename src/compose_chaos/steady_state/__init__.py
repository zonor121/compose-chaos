"""Верификация устойчивого состояния.

Три фазы (отражены в steady_state_checks.phase):
- before  — до атак: стенд обязан быть устойчивым, иначе прогон не стартует;
- during  — наблюдение под атакой (нарушение = инцидент, см. incidents);
- after   — после отката: критерий успеха прогона (MTTR считается как
  время до возврата устойчивого состояния).

TODO(Этап 3): реализовать run_phase(phase) на HttpProbe + правило
«N успешных проб подряд за окно».
"""

from __future__ import annotations

from typing import Any

from compose_chaos.models.scenario import Scenario


class SteadyStateVerifier:
    def __init__(self, scenario: Scenario, gateway: Any) -> None:
        self.scenario = scenario
        self.gateway = gateway

    async def run_phase(self, phase: str) -> bool:
        """Выполняет проверки фазы; True — устойчивое состояние подтверждено."""
        raise NotImplementedError("Этап 3")
