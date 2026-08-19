from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum

type TimerId = int
type AddTimer = Callable[[int, Callable[[], bool]], TimerId]
type RemoveTimer = Callable[[TimerId], object]


class SchedulerState(StrEnum):
    STOPPED = "Parado"
    RUNNING = "Ativo"
    PAUSED = "Pausado"


class ReminderScheduler:
    """Controla um único timer periódico, sem depender diretamente do GTK."""

    def __init__(self, add_timer: AddTimer, remove_timer: RemoveTimer) -> None:
        self._add_timer = add_timer
        self._remove_timer = remove_timer
        self._timer_id: TimerId | None = None
        self._interval_seconds: int | None = None
        self._callback: Callable[[], None] | None = None
        self.state = SchedulerState.STOPPED

    def start(self, interval_seconds: int, callback: Callable[[], None]) -> None:
        if interval_seconds <= 0:
            raise ValueError("O intervalo deve ser maior que zero.")
        self.stop()
        self._interval_seconds = interval_seconds
        self._callback = callback
        self._schedule()
        self.state = SchedulerState.RUNNING

    def pause(self) -> None:
        if self.state is not SchedulerState.RUNNING:
            return
        self._cancel_timer()
        self.state = SchedulerState.PAUSED

    def resume(self) -> None:
        if self.state is not SchedulerState.PAUSED:
            return
        self._schedule()
        self.state = SchedulerState.RUNNING

    def stop(self) -> None:
        self._cancel_timer()
        self._interval_seconds = None
        self._callback = None
        self.state = SchedulerState.STOPPED

    def _schedule(self) -> None:
        if self._interval_seconds is None or self._callback is None:
            raise RuntimeError("O agendador não possui configuração ativa.")
        milliseconds = self._interval_seconds * 1_000
        self._timer_id = self._add_timer(milliseconds, self._on_timeout)

    def _cancel_timer(self) -> None:
        if self._timer_id is not None:
            self._remove_timer(self._timer_id)
            self._timer_id = None

    def _on_timeout(self) -> bool:
        if self.state is not SchedulerState.RUNNING or self._callback is None:
            return False
        self._callback()
        return True
