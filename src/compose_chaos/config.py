"""Конфигурация приложения (12-factor: окружение > .env > значения по умолчанию)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CHAOS_", env_file=".env", extra="ignore")

    # local-first: по умолчанию PostgreSQL в compose-сети самого инструмента;
    # профиль минимальной установки: sqlite+aiosqlite:///./chaos.db
    database_url: str = "postgresql+asyncpg://chaos:chaos@localhost:5433/chaos"

    # Каталог для HTML/JSON отчётов
    output_dir: Path = Path("out")

    # Интервал съёма Docker-статистики, сек
    stats_interval_sec: float = 5.0

    # Таймаут HTTP-проб, сек
    probe_timeout_sec: float = 5.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
