"""WebSocket: живой стрим событий прогона для UI.

Канал /ws/runs/{run_id}: оркестратор публикует переходы FSM, вердикты проб,
инциденты; UI перерисовывает статусы узлов графа (зелёный/жёлтый/красный,
молния у атакуемого сервиса).

Альтернатива (если WebSocket окажется избыточен): SSE — однонаправленный
стрим простее и совместимее с прокси.
"""

from __future__ import annotations

from fastapi import APIRouter, WebSocket

router = APIRouter()


@router.websocket("/ws/runs/{run_id}")
async def run_events(websocket: WebSocket, run_id: int) -> None:
    await websocket.accept()
    # TODO(Этап 4): подписка на очередь событий оркестратора (asyncio.Queue)
    await websocket.send_json({"run_id": run_id, "event": "stub", "detail": "Этап 4"})
    await websocket.close()
