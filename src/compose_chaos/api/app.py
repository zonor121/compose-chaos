"""Приложение FastAPI: REST + WebSocket + статический UI.

TODO(Этап 4): подключить routers (routes_runs, ws), смонтировать
compose_chaos/ui как StaticFiles(directory=..., html=True),
lifespan: инициализация engine/sessionmaker из config.
"""

from __future__ import annotations

from fastapi import FastAPI

from compose_chaos import __version__

app = FastAPI(
    title="compose-chaos API",
    version=__version__,
    description="API инструмента хаос-инженерии для docker-compose сред",
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness-эндпоинт самого инструмента."""
    return {"status": "ok", "version": __version__}


# TODO(Этап 4):
# app.include_router(runs.router, prefix="/api")
# app.include_router(ws.router)
# app.mount("/", StaticFiles(directory=ui_path, html=True))
