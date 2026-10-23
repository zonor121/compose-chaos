# compose-chaos

Инструмент хаос-инженерии для локальных сред на основе docker-compose:
планово «ломает» приложение (kill/pause контейнеров, сетевые деградации через
`tc netem`, ресурсный стресс), наблюдает за реакцией (HTTP-пробы, Docker-статистика)
и формирует отчёты с MTTD/MTTR.

Статус: **скелет проекта** — структура модулей и декларативные части
(DSL-модели, FSM, реестр атак, ORM-схема) реализованы, бизнес-логика помечена TODO.

## Структура

```
compose-chaos/
├── pyproject.toml            # стек и настройки инструментов качества
├── .devcontainer/            # окружение для GitHub Codespaces (Docker-in-Docker)
├── src/compose_chaos/
│   ├── cli.py                # CLI: validate / run / report / serve
│   ├── config.py             # настройки (pydantic-settings)
│   ├── models/
│   │   ├── scenario.py       # DSL сценария хаоса (Pydantic)  ← реализовано
│   │   └── compose.py        # парсинг compose-файла (топология) ← реализовано
│   ├── orchestrator/
│   │   ├── fsm.py            # конечный автомат прогона          ← переходы реализованы
│   │   └── runner.py         # asyncio.TaskGroup: prepare→attack→verify→rollback
│   ├── attacks/              # плагинные адаптеры атак
│   │   ├── base.py           # ABC + реестр                     ← реализовано
│   │   ├── lifecycle.py      # container.kill / pause / stop
│   │   ├── netem.py          # tc netem через sidecar (network_mode: service:target)
│   │   ├── stress.py         # stress-ng + docker update (лимиты cgroup)
│   │   └── toxiproxy.py      # userspace-fallback без привилегий
│   ├── docker/               # обёртка docker-py: клиент + стрим статистики
│   ├── probes/               # HTTP-пробы (httpx)
│   ├── steady_state/         # верификация устойчивого состояния
│   ├── store/                # SQLAlchemy 2.0 async + Alembic
│   │   ├── models.py         # 10 таблиц (см. docs/er-diagram.png) ← реализовано
│   │   └── migrations/       # env.py + versions/
│   ├── reports/              # Jinja2 → HTML, Pydantic → JSON
│   ├── api/                  # FastAPI: /api/runs, /health, WebSocket
│   └── ui/                   # ванильный JS + Cytoscape.js (граф топологии)
├── scenarios/                # YAML-сценарии хаоса
├── demoapp/                  # демо-приложение — полигон атак
├── tests/                    # pytest (модели, реестр, FSM)
└── docs/                     # ER-диаграмма, описание DSL
```

## Быстрый старт

```bash
python3.14 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest                                        # тесты скелета
compose-chaos validate scenarios/example_db_kill.yaml   # проверка сценария
docker compose -f demoapp/docker-compose.yml up -d      # поднять полигон
```

## База данных

По умолчанию PostgreSQL 16 поднимается рядом (см. `demoapp/docker-compose.yml`,
сервис `chaos-db` можно вынести в отдельный compose-файл инструмента).
Профиль минимальной установки: `CHAOS_DATABASE_URL=sqlite+aiosqlite:///./chaos.db`.
Миграции: `alembic revision --autogenerate` → `alembic upgrade head`.

## Окружение без прав администратора (защита)

`.devcontainer/devcontainer.json` поднимает проект в GitHub Codespaces
с Docker-in-Docker. Нюанс: модуль ядра `sch_netem` внутри DinD может быть
недоступен — адаптер `netem` обязан проверить доступность через
`check_available()` и предложить fallback (`toxiproxy`). Проверить заранее:

```bash
docker run --rm --cap-add NET_ADMIN busybox tc qdisc add dev eth0 root netem delay 100ms
```

## План этапов

1. Скелет, DSL, схема БД ← текущий
2. Ядро: DockerGateway, адаптеры lifecycle/netem/stress, оркестратор (FSM)
3. Наблюдение: stats-стрим, HTTP-пробы, steady-state, инциденты (MTTD/MTTR)
4. Отчёты (HTML/JSON), API + UI (граф топологии, живой статус прогона)
5. Эксперименты (глава 3 ВКР): прогон на 10–15 open-source compose-проектах
