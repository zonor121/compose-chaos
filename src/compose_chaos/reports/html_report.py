"""HTML-отчёт по прогону: Jinja2-шаблон + Chart.js, статический файл.

Отчёт открывается двойным кликом (без сервера), поэтому данные встраиваются
в HTML как inline JSON. Разделы: сводка прогона, таймлайн атак, графики
латентности проб и потребления ресурсов, таблица инцидентов с MTTD/MTTR.

TODO(Этап 4): собрать данные прогона из store, передать в шаблон,
записать в Settings.output_dir и зарегистрировать в reports (таблица).
"""

from __future__ import annotations

from pathlib import Path

from compose_chaos.config import get_settings


class HtmlReporter:
    def __init__(self, run_id: int) -> None:
        self.run_id = run_id
        self.settings = get_settings()

    def render(self) -> Path:
        """Рендерит отчёт и возвращает путь к файлу."""
        raise NotImplementedError("Этап 4")
