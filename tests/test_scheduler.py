from collections.abc import Callable

import pytest

from lembrete_agua.scheduler import ReminderScheduler, SchedulerState


class FakeTimers:
    def __init__(self) -> None:
        self.callbacks: dict[int, Callable[[], bool]] = {}
        self.intervals: list[int] = []
        self.removed: list[int] = []

    def add(self, interval: int, callback: Callable[[], bool]) -> int:
        timer_id = len(self.intervals) + 1
        self.intervals.append(interval)
        self.callbacks[timer_id] = callback
        return timer_id

    def remove(self, timer_id: int) -> None:
        self.removed.append(timer_id)
        self.callbacks.pop(timer_id, None)


def test_start_schedules_without_triggering_immediately() -> None:
    timers = FakeTimers()
    reminders: list[str] = []
    scheduler = ReminderScheduler(timers.add, timers.remove)

    scheduler.start(60, lambda: reminders.append("sent"))

    assert scheduler.state is SchedulerState.RUNNING
    assert timers.intervals == [60_000]
    assert reminders == []
    assert timers.callbacks[1]() is True
    assert reminders == ["sent"]


def test_start_replaces_existing_timer_to_avoid_duplicates() -> None:
    timers = FakeTimers()
    scheduler = ReminderScheduler(timers.add, timers.remove)

    scheduler.start(60, lambda: None)
    scheduler.start(120, lambda: None)

    assert timers.removed == [1]
    assert list(timers.callbacks) == [2]
    assert timers.intervals == [60_000, 120_000]


def test_pause_and_resume_manage_one_timer() -> None:
    timers = FakeTimers()
    scheduler = ReminderScheduler(timers.add, timers.remove)
    scheduler.start(60, lambda: None)

    scheduler.pause()
    scheduler.pause()
    assert scheduler.state is SchedulerState.PAUSED
    assert timers.removed == [1]

    scheduler.resume()
    scheduler.resume()
    assert scheduler.state is SchedulerState.RUNNING
    assert list(timers.callbacks) == [2]


def test_invalid_interval_is_rejected() -> None:
    timers = FakeTimers()
    scheduler = ReminderScheduler(timers.add, timers.remove)

    with pytest.raises(ValueError, match="maior que zero"):
        scheduler.start(0, lambda: None)


def test_remaining_time_is_preserved_while_paused() -> None:
    timers = FakeTimers()
    current_time = [100.0]
    scheduler = ReminderScheduler(timers.add, timers.remove, lambda: current_time[0])
    scheduler.start(60, lambda: None)

    current_time[0] = 115.0
    assert scheduler.remaining_seconds == 45.0
    scheduler.pause()
    current_time[0] = 130.0
    assert scheduler.remaining_seconds == 45.0

    scheduler.resume()
    assert timers.intervals[-1] == 45_000
