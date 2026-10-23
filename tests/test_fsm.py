"""Тесты конечного автомата прогона."""

from __future__ import annotations

import pytest

from compose_chaos.orchestrator.fsm import FSM, FSMState, InvalidTransition


def test_happy_path() -> None:
    fsm = FSM()
    fsm.transition(FSMState.ATTACK)
    fsm.transition(FSMState.VERIFY)
    fsm.transition(FSMState.ROLLBACK)
    fsm.transition(FSMState.DONE)
    assert fsm.is_terminal()
    assert len(fsm.history) == 4


def test_illegal_transition_rejected() -> None:
    fsm = FSM()
    with pytest.raises(InvalidTransition):
        fsm.transition(FSMState.DONE)  # PREPARE → DONE запрещён


def test_failure_is_possible_from_any_active_state() -> None:
    for path in ([FSMState.ATTACK],
                 [FSMState.ATTACK, FSMState.VERIFY],
                 [FSMState.ATTACK, FSMState.ROLLBACK]):
        fsm = FSM()
        for state in path:
            fsm.transition(state)
        fsm.transition(FSMState.FAILED)
        assert fsm.is_terminal()
