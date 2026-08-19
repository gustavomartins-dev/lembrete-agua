from datetime import UTC, datetime, timedelta
from pathlib import Path

from lembrete_agua.analytics import period_stats
from lembrete_agua.history import HistoryStore, ReminderRecord, ReminderStatus


def make_record(
    identifier: str,
    status: ReminderStatus,
    when: datetime,
    milliliters: int = 125,
) -> ReminderRecord:
    return ReminderRecord(
        id=identifier,
        session_id="session",
        scheduled_at=when.isoformat(),
        sips=5,
        milliliters=milliliters,
        status=status,
    )


def test_history_adds_and_responds_to_reminder(tmp_path: Path) -> None:
    store = HistoryStore(tmp_path / "history.json")
    record = ReminderRecord.create("session", 5, 125)
    store.add(record)

    assert store.get(record.id) == record
    updated = store.respond(record.id, True)

    assert updated is not None
    assert updated.status is ReminderStatus.DRANK
    assert updated.responded_at is not None
    assert store.get(record.id) == updated


def test_invalid_history_entries_are_ignored(tmp_path: Path) -> None:
    path = tmp_path / "history.json"
    path.write_text('[{"invalid": true}, "text"]', encoding="utf-8")
    assert HistoryStore(path).load() == []


def test_period_stats_calculates_weekly_performance() -> None:
    now = datetime(2026, 8, 20, tzinfo=UTC)
    records = [
        make_record("1", ReminderStatus.DRANK, now - timedelta(days=1)),
        make_record("2", ReminderStatus.SKIPPED, now - timedelta(days=2)),
        make_record("3", ReminderStatus.PENDING, now - timedelta(days=3)),
        make_record("4", ReminderStatus.DRANK, now - timedelta(days=10)),
    ]

    stats = period_stats(records, 7, now=now)

    assert stats.consumed_ml == 125
    assert stats.confirmed == 1
    assert stats.skipped == 1
    assert stats.performance_percent == 50
