"""REST-роуты прогонов.

Планируемые эндпоинты (Этап 4):
- GET  /api/runs                — список прогонов (фильтр по сценарию/статусу);
- GET  /api/runs/{run_id}       — детали прогона + инциденты + агрегаты;
- POST /api/runs                — запуск сценария (run в фоне, статус через WS);
- GET  /api/scenarios           — сохранённые сценарии;
- GET  /api/topology/{project}  — нормализованная топология для UI-графа
                                  (ComposeProject.parse → узлы и depends_on-рёбра).
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/runs")
async def list_runs() -> list[dict]:
    """TODO(Этап 4): выборка из store.runs."""
    return []
