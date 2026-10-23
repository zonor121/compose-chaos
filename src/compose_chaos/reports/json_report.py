"""JSON-отчёт по прогону: машинно-читаемый снимок для CI-интеграций.

Формат = сериализация Pydantic-модели RunReport (TODO, Этап 4):
метаданные прогона, план атак, инциденты с MTTD/MTTR, агрегаты проб.
JSON Schema отчёта экспортируется для валидации во внешних пайплайнах.
"""

from __future__ import annotations

from pathlib import Path

from compose_chaos.config import get_settings


class JsonReporter:
    def __init__(self, run_id: int) -> None:
        self.run_id = run_id
        self.settings = get_settings()

    def render(self) -> Path:
        raise NotImplementedError("Этап 4")
