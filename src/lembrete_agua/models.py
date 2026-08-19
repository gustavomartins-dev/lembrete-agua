from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class IntervalUnit(StrEnum):
    MINUTES = "minutos"
    HOURS = "horas"


@dataclass(frozen=True, slots=True)
class Preferences:
    interval: int = 30
    unit: IntervalUnit = IntervalUnit.MINUTES
    sips: int = 5
    autostart: bool = False

    @property
    def interval_seconds(self) -> int:
        multiplier = 60 if self.unit is IntervalUnit.MINUTES else 3_600
        return self.interval * multiplier

