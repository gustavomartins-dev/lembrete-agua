from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from time import monotonic

type TimerId = int
type AddTimer = Callable[[int, Callable[[], bool]], TimerId]
type RemoveTimer = Callable[[TimerId], object]


class SchedulerState(StrEnum):
    STOPPED = "Parado"
    RUNNING = "Ativo"
    PAUSED = "Pausado"


class ReminderScheduler:
    """Controla um único timer periódico, sem depender diretamente do GTK."""

    def __init__(
        self,
        add_timer: AddTimer,
        remove_timer: RemoveTimer,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self._add_timer = add_timer
        self._remove_timer = remove_timer
        self._clock = clock
        self._timer_id: TimerId | None = None
        self._interval_seconds: float | None = None
        self._callback: Callable[[], None] | None = None
        self._deadline: float | None = None
        self._paused_remaining: float | None = None
        self.state = SchedulerState.STOPPED

    @property
    def remaining_seconds(self) -> float | None:
        if self.state is SchedulerState.PAUSED:
            return self._paused_remaining
        if self.state is SchedulerState.RUNNING and self._deadline is not None:
            return max(0.0, self._deadline - self._clock())
        return None

    def start(self, interval_seconds: float, callback: Callable[[], None]) -> None:
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
        self._paused_remaining = self.remaining_seconds
        self._cancel_timer()
        self.state = SchedulerState.PAUSED

    def resume(self) -> None:
        if self.state is not SchedulerState.PAUSED:
            return
        self._schedule(self._paused_remaining)
        self._paused_remaining = None
        self.state = SchedulerState.RUNNING

    def reset_countdown(self) -> bool:
        """Volta o próximo disparo ao intervalo completo, preservando o estado."""
        if self.state is SchedulerState.STOPPED or self._interval_seconds is None:
            return False
        if self.state is SchedulerState.PAUSED:
            self._paused_remaining = self._interval_seconds
        else:
            self._cancel_timer()
            self._schedule()
        return True

    def stop(self) -> None:
        self._cancel_timer()
        self._interval_seconds = None
        self._callback = None
        self._deadline = None
        self._paused_remaining = None
        self.state = SchedulerState.STOPPED

    def _schedule(self, delay_seconds: float | None = None) -> None:
        if self._interval_seconds is None or self._callback is None:
            raise RuntimeError("O agendador não possui configuração ativa.")
        delay = delay_seconds if delay_seconds is not None else self._interval_seconds
        milliseconds = max(1, round(delay * 1_000))
        self._deadline = self._clock() + delay
        self._timer_id = self._add_timer(milliseconds, self._on_timeout)

    def _cancel_timer(self) -> None:
        if self._timer_id is not None:
            self._remove_timer(self._timer_id)
            self._timer_id = None
        self._deadline = None

    def _on_timeout(self) -> bool:
        if self.state is not SchedulerState.RUNNING or self._callback is None:
            return False
        self._deadline = self._clock() + (self._interval_seconds or 0)
        self._callback()
        return self.state is SchedulerState.RUNNING and self._timer_id is not None
