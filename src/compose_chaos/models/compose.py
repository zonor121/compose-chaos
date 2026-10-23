"""Парсинг docker-compose файла: топология для UI-графа и планирования атак.

Инструмент использует только метаданные compose-файла (сервисы, depends_on,
сети, healthcheck) — трафик не перехватывается и не анализируется.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ComposeService(BaseModel):
    """Сервис из compose-файла в нормализованном виде."""

    name: str
    image: str | None = None
    depends_on: list[str] = Field(default_factory=list)
    networks: list[str] = Field(default_factory=list)
    has_healthcheck: bool = False


class ComposeProject(BaseModel):
    """Нормализованное представление compose-проекта."""

    name: str | None = None
    services: list[ComposeService] = Field(default_factory=list)
    networks: list[str] = Field(default_factory=list)

    @classmethod
    def parse(cls, path: str | Path) -> "ComposeProject":
        """Читает compose-файл и приводит depends_on к списку имён сервисов.

        depends_on в compose-spec бывает трёх форм: строка, список строк,
        отображение {name: {condition: ...}} — все сводятся к списку.
        """
        with open(path, encoding="utf-8") as fh:
            raw: dict[str, Any] = yaml.safe_load(fh) or {}

        def _names(dep: Any) -> list[str]:
            if dep is None:
                return []
            if isinstance(dep, str):
                return [dep]
            if isinstance(dep, list):
                return [str(d) for d in dep]
            if isinstance(dep, dict):
                return [str(k) for k in dep]
            raise ValueError(f"неподдерживаемая форма depends_on: {type(dep)!r}")

        services = [
            ComposeService(
                name=str(name),
                image=(spec or {}).get("image"),
                depends_on=_names((spec or {}).get("depends_on")),
                networks=_names((spec or {}).get("networks")),
                has_healthcheck="healthcheck" in (spec or {}),
            )
            for name, spec in (raw.get("services") or {}).items()
        ]
        networks = [str(n) for n in (raw.get("networks") or {})]
        return cls(name=raw.get("name"), services=services, networks=networks)

    def edges(self) -> list[tuple[str, str]]:
        """Рёбра зависимостей (depends_on) — основа графа в UI."""
        return [(dep, svc.name) for svc in self.services for dep in svc.depends_on]
