from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from lembrete_agua.history import ReminderRecord, ReminderStatus


@dataclass(frozen=True, slots=True)
class PeriodStats:
    consumed_ml: int
    confirmed: int
    skipped: int

    @property
    def performance_percent(self) -> int:
        answered = self.confirmed + self.skipped
        return round(self.confirmed * 100 / answered) if answered else 0


def period_stats(
    records: list[ReminderRecord],
    days: int,
    *,
    now: datetime | None = None,
) -> PeriodStats:
    reference = now or datetime.now(UTC)
    cutoff = reference - timedelta(days=days)
    selected = [record for record in records if _date(record) >= cutoff]
    confirmed = [record for record in selected if record.status is ReminderStatus.DRANK]
    return PeriodStats(
        consumed_ml=sum(record.milliliters for record in confirmed),
        confirmed=len(confirmed),
        skipped=sum(record.status is ReminderStatus.SKIPPED for record in selected),
    )


def _date(record: ReminderRecord) -> datetime:
    parsed = datetime.fromisoformat(record.scheduled_at)
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)
