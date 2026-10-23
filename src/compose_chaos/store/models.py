"""ORM-модели: 10 таблиц инструмента (см. docs/er-diagram.png).

Схема «runs — центральная сущность»: все наблюдения и исходы прогона
ссылаются на runs.id. Справочники окружений и сценариев — projects,
scenarios. Перечислимые значения хранятся строками (VARCHAR) — схема
остаётся переносимой между PostgreSQL и SQLite-профилем.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def _ts() -> DateTime:
    return DateTime(timezone=True)


class Project(Base):
    """docker-compose окружение, которое тестируем."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    compose_path: Mapped[str] = mapped_column(Text)
    compose_hash: Mapped[str | None] = mapped_column(String(64))  # sha256 файла
    created_at: Mapped[datetime] = mapped_column(_ts(), server_default=func.now())


class Scenario(Base):
    """Сценарий хаоса (YAML DSL хранится целиком)."""

    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String(120))
    yaml_body: Mapped[str] = mapped_column(Text)
    schema_version: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(_ts(), server_default=func.now())


class Run(Base):
    """Прогон сценария: центральная сущность схемы."""

    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scenario_id: Mapped[int] = mapped_column(ForeignKey("scenarios.id"))
    status: Mapped[str] = mapped_column(String(16))  # running|completed|failed|aborted
    started_at: Mapped[datetime] = mapped_column(_ts(), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(_ts(), nullable=True)
    config_snapshot: Mapped[str | None] = mapped_column(Text)  # JSONB/JSON-снимок


class Attack(Base):
    """Факт выполнения атаки в прогоне."""

    __tablename__ = "attacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    attack_type: Mapped[str] = mapped_column(String(32))
    target_service: Mapped[str] = mapped_column(String(120))
    params: Mapped[str | None] = mapped_column(Text)  # JSON
    status: Mapped[str] = mapped_column(String(16))   # injected|rolled_back|failed
    injected_at: Mapped[datetime | None] = mapped_column(_ts(), nullable=True)
    rolled_back_at: Mapped[datetime | None] = mapped_column(_ts(), nullable=True)


class Event(Base):
    """Журнал событий оркестратора (переходы FSM, ошибки, откаты)."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    attack_id: Mapped[int | None] = mapped_column(ForeignKey("attacks.id"), nullable=True)
    level: Mapped[str] = mapped_column(String(8))     # info|warn|error
    fsm_state: Mapped[str | None] = mapped_column(String(16))
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(_ts(), server_default=func.now())


class MetricSample(Base):
    """Временной ряд Docker-статистики по сервисам прогона."""

    __tablename__ = "metric_samples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    service_name: Mapped[str] = mapped_column(String(120))
    ts: Mapped[datetime] = mapped_column(_ts())
    cpu_percent: Mapped[float] = mapped_column(Float)
    mem_usage_mb: Mapped[float] = mapped_column(Float)
    net_io_kbps: Mapped[float] = mapped_column(Float)


class ProbeResult(Base):
    """Результат HTTP-пробы мониторинга."""

    __tablename__ = "probe_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    service_name: Mapped[str] = mapped_column(String(120))
    ts: Mapped[datetime] = mapped_column(_ts())
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float)
    ok: Mapped[bool] = mapped_column(Integer)  # boolean, переносимо в SQLite


class SteadyStateCheck(Base):
    """Вердикт проверки устойчивого состояния (before/during/after)."""

    __tablename__ = "steady_state_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    phase: Mapped[str] = mapped_column(String(8))  # before|during|after
    name: Mapped[str] = mapped_column(String(120))
    passed: Mapped[bool] = mapped_column(Integer)
    ts: Mapped[datetime] = mapped_column(_ts(), server_default=func.now())


class Incident(Base):
    """Обнаруженный отказ: MTTD = detected_at − injected_at,
    MTTR = recovered_at − detected_at."""

    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    attack_id: Mapped[int | None] = mapped_column(ForeignKey("attacks.id"), nullable=True)
    service_name: Mapped[str] = mapped_column(String(120))
    detected_at: Mapped[datetime] = mapped_column(_ts())
    recovered_at: Mapped[datetime | None] = mapped_column(_ts(), nullable=True)
    severity: Mapped[str] = mapped_column(String(16))  # minor|major|critical


class Report(Base):
    """Метаданные сгенерированного отчёта (HTML-файл / JSON)."""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    format: Mapped[str] = mapped_column(String(8))  # html|json
    file_path: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)  # JSON: MTTD/MTTR-агрегаты
    generated_at: Mapped[datetime] = mapped_column(_ts(), server_default=func.now())
