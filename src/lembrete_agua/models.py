from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

MILLILITERS_PER_SIP = 25
MAX_SIPS_PER_REMINDER = 5


class DurationUnit(StrEnum):
    MINUTES = "minutos"
    HOURS = "horas"


@dataclass(frozen=True, slots=True)
class Preferences:
    target_ml: int = 500
    duration: int = 2
    unit: DurationUnit = DurationUnit.HOURS
    autostart: bool = True

    @property
    def duration_seconds(self) -> int:
        multiplier = 60 if self.unit is DurationUnit.MINUTES else 3_600
        return self.duration * multiplier


@dataclass(frozen=True, slots=True)
class HydrationPlan:
    target_ml: int
    duration_seconds: int
    total_sips: int
    reminder_count: int
    interval_seconds: float

    def sips_for_reminder(self, reminder_number: int) -> int:
        if not 1 <= reminder_number <= self.reminder_count:
            raise ValueError("Número de lembrete fora do plano.")
        already_allocated = (reminder_number - 1) * MAX_SIPS_PER_REMINDER
        return min(MAX_SIPS_PER_REMINDER, self.total_sips - already_allocated)

    def milliliters_for_reminder(self, reminder_number: int) -> int:
        if reminder_number == self.reminder_count:
            allocated = sum(
                self.sips_for_reminder(current) * MILLILITERS_PER_SIP
                for current in range(1, reminder_number)
            )
            return self.target_ml - allocated
        return self.sips_for_reminder(reminder_number) * MILLILITERS_PER_SIP


def build_hydration_plan(preferences: Preferences) -> HydrationPlan:
    total_sips = math.ceil(preferences.target_ml / MILLILITERS_PER_SIP)
    reminder_count = math.ceil(total_sips / MAX_SIPS_PER_REMINDER)
    return HydrationPlan(
        target_ml=preferences.target_ml,
        duration_seconds=preferences.duration_seconds,
        total_sips=total_sips,
        reminder_count=reminder_count,
        interval_seconds=preferences.duration_seconds / reminder_count,
    )
