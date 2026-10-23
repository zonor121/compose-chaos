"""Адаптеры атак: плагинная подсистема внедрения дефектов.

Импорт модулей ниже запускает декораторы @register и наполняет реестр.
"""

from compose_chaos.attacks import lifecycle, netem, stress, toxiproxy  # noqa: F401
from compose_chaos.attacks.base import AttackAdapter, available_types, get_adapter, register

__all__ = ["AttackAdapter", "available_types", "get_adapter", "register"]
