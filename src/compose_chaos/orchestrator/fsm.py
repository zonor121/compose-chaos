"""Конечный автомат прогона.

Цикл: PREPARE → ATTACK → VERIFY → ROLLBACK → DONE (или FAILED на любом шаге).
Переходы валидируются таблицей ALLOWED_TRANSITIONS; история переходов
сохраняется в journal (потом пишется в таблицу events).
"""

from __future__ import annotations

from enum import StrEnum


class FSMState(StrEnum):
    PREPARE = "prepare"      # подъём стенда, проверка steady_state до атаки
    ATTACK = "attack"        # внедрение атак по плану сценария
    VERIFY = "verify"        # наблюдение: пробы, статистика, детекция инцидентов
    ROLLBACK = "rollback"    # откат атак, восстановление стенда
    DONE = "done"            # успешное завершение прогона
    FAILED = "failed"        # авария инструмента или нарушение устойчивого состояния


ALLOWED_TRANSITIONS: dict[FSMState, set[FSMState]] = {
    FSMState.PREPARE: {FSMState.ATTACK, FSMState.FAILED},
    FSMState.ATTACK: {FSMState.VERIFY, FSMState.ROLLBACK, FSMState.FAILED},
    FSMState.VERIFY: {FSMState.ROLLBACK, FSMState.DONE, FSMState.FAILED},
    FSMState.ROLLBACK: {FSMState.DONE, FSMState.FAILED},
    FSMState.DONE: set(),
    FSMState.FAILED: set(),
}


class InvalidTransition(RuntimeError):
    """Попытка недопустимого перехода FSM."""


class FSM:
    """Автомат одного прогона. Потокобезопасность не требуется: драйвит одна задача."""

    def __init__(self) -> None:
        self.state: FSMState = FSMState.PREPARE
        self.history: list[tuple[FSMState, FSMState]] = []

    def can(self, target: FSMState) -> bool:
        return target in ALLOWED_TRANSITIONS[self.state]

    def transition(self, target: FSMState) -> FSMState:
        if not self.can(target):
            raise InvalidTransition(f"переход {self.state} → {target} запрещён")
        self.history.append((self.state, target))
        self.state = target
        return self.state

    def is_terminal(self) -> bool:
        return not ALLOWED_TRANSITIONS[self.state]
