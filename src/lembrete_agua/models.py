from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

MILLILITERS_PER_SIP = 25


class TimeUnit(StrEnum):
    MINUTES = "minutos"
    HOURS = "horas"


class PlanMode(StrEnum):
    MANUAL = "manual"
    AUTOMATIC = "automatico"


class PlanStrategy(StrEnum):
    LIGHT = "leve"
    BALANCED = "equilibrado"
    INTENSIVE = "intensivo"

    @property
    def max_sips(self) -> int:
        return {
            PlanStrategy.LIGHT: 3,
            PlanStrategy.BALANCED: 5,
            PlanStrategy.INTENSIVE: 8,
        }[self]


@dataclass(frozen=True, slots=True)
class Preferences:
    sips: int = 5
    interval: int = 30
    unit: TimeUnit = TimeUnit.MINUTES
    target_ml: int = 500
    duration: int = 2
    duration_unit: TimeUnit = TimeUnit.HOURS
    plan_mode: PlanMode = PlanMode.MANUAL
    strategy: PlanStrategy = PlanStrategy.BALANCED
    autostart: bool = True

    @property
    def interval_seconds(self) -> int:
        return self.interval * (60 if self.unit is TimeUnit.MINUTES else 3_600)

    @property
    def duration_seconds(self) -> int:
        return self.duration * (60 if self.duration_unit is TimeUnit.MINUTES else 3_600)


@dataclass(frozen=True, slots=True)
class HydrationPlan:
    interval_seconds: float
    fixed_sips: int
    target_ml: int | None = None
    total_sips: int | None = None
    reminder_count: int | None = None
    strategy: PlanStrategy | None = None

    @property
    def is_repeating(self) -> bool:
        return self.reminder_count is None

    def sips_for_reminder(self, reminder_number: int) -> int:
        if reminder_number < 1 or (
            self.reminder_count is not None and reminder_number > self.reminder_count
        ):
            raise ValueError("Número de lembrete fora do plano.")
        if self.reminder_count is None or self.total_sips is None:
            return self.fixed_sips
        already_allocated = (reminder_number - 1) * self.fixed_sips
        return min(self.fixed_sips, self.total_sips - already_allocated)

    def milliliters_for_reminder(self, reminder_number: int) -> int:
        sips = self.sips_for_reminder(reminder_number)
        if self.reminder_count is not None and reminder_number == self.reminder_count:
            allocated = (reminder_number - 1) * self.fixed_sips * MILLILITERS_PER_SIP
            return (self.target_ml or 0) - allocated
        return sips * MILLILITERS_PER_SIP


def build_manual_plan(preferences: Preferences) -> HydrationPlan:
    return HydrationPlan(
        interval_seconds=preferences.interval_seconds,
        fixed_sips=preferences.sips,
    )


def build_hydration_plan(
    preferences: Preferences,
    strategy: PlanStrategy | None = None,
) -> HydrationPlan:
    selected = strategy or preferences.strategy
    total_sips = math.ceil(preferences.target_ml / MILLILITERS_PER_SIP)
    reminder_count = math.ceil(total_sips / selected.max_sips)
    return HydrationPlan(
        target_ml=preferences.target_ml,
        total_sips=total_sips,
        reminder_count=reminder_count,
        interval_seconds=preferences.duration_seconds / reminder_count,
        fixed_sips=selected.max_sips,
        strategy=selected,
    )
