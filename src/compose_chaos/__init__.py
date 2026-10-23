"""compose-chaos — инструмент хаос-инженерии для локальных docker-compose сред.

Модули верхнего уровня:
- models         — DSL сценариев и парсинг compose-топологии (Pydantic);
- orchestrator   — конечный автомат прогона и исполнитель (asyncio.TaskGroup);
- attacks        — плагинные адаптеры атак (lifecycle, netem, stress, toxiproxy);
- docker         — обёртка Docker SDK (клиент, стрим статистики);
- probes         — HTTP-пробы;
- steady_state   — верификация устойчивого состояния;
- store          — SQLAlchemy 2.0 async + Alembic (10 таблиц, см. docs/er-diagram.png);
- reports        — генерация HTML/JSON отчётов;
- api / ui       — FastAPI-бэкенд и веб-интерфейс (Cytoscape.js).
"""

__version__ = "0.1.0"
