# DSL сценария хаоса (v1)

Схема валидируется Pydantic (`src/compose_chaos/models/scenario.py`);
JSON Schema для редакторов: `Scenario.to_json_schema()`.

## Корневые поля

| Поле | Тип | По умолчанию | Описание |
|---|---|---|---|
| `schema_version` | int | 1 | версия DSL |
| `name` | str, 1–120 | — | имя сценария |
| `description` | str | "" | человекочитаемое описание |
| `compose_file` | path | — | docker-compose.yml тестируемого приложения |
| `steady_state` | list[ProbeSpec] | [] | проверки до атаки / после отката |
| `attacks` | list[AttackStep], ≥1 | — | план атак (выполняются по порядку) |
| `monitoring` | MonitoringSpec | — | интервал статистики + пробы во время атаки |
| `rollback_on_breach` | bool | true | немедленный откат при нарушении устойчивого состояния |
| `total_duration_sec` | int? | null | жёсткий лимит длительности прогона |

## Каталог атак (AttackType)

| Тип | Адаптер | Параметры (params) |
|---|---|---|
| `container.kill` | lifecycle.KillService | `signal` (SIGKILL) |
| `container.pause` | lifecycle.PauseService | — |
| `container.stop` | lifecycle.StopService | `timeout` |
| `netem.delay` | netem.DelayService | `delay_ms`, `jitter_ms` |
| `netem.loss` | netem.LossService | `loss_percent` |
| `netem.partition` | netem.PartitionService | — (изоляция netns) |
| `stress.cpu` | stress.CpuStress | `workers`, `load_percent` |
| `stress.memory` | stress.MemoryStress | `workers`, `load_percent` |
| `stress.disk` | stress.DiskStress | `fill_percent` |
| `toxiproxy.custom` | toxiproxy.ToxiproxyAttack | `toxin`, `attributes` |

## Общие поля AttackStep

`name`, `type`, `target` (сервис compose), `params`, `duration_sec` (время
воздействия до отката), `enabled`.

## Проба (ProbeSpec)

`name`, `url`, `expect.status` (200), `expect.body_contains`,
`expect.max_latency_ms`, `interval_sec`.

## Расширение (v2, TODO)

Типизированные параметры атак через discriminated union; секция `schedule`
(последовательность/параллельность атак); условия остановки (`stop_if`).
