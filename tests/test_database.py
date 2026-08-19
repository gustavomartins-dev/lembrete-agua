from pathlib import Path

from lembrete_agua.database import ActiveSession, ActiveSessionStore, Database


def test_active_session_survives_new_store_instance(tmp_path: Path) -> None:
    database = Database(tmp_path / "state.sqlite3")
    expected = ActiveSession(
        session_id="session-1",
        reminder_number=2,
        interval_seconds=1_200,
        deadline=2_000.0,
        paused_remaining=None,
        state="Ativo",
    )

    ActiveSessionStore(database).save(expected)

    assert ActiveSessionStore(Database(database.path)).load() == expected


def test_active_session_can_be_cleared(tmp_path: Path) -> None:
    store = ActiveSessionStore(Database(tmp_path / "state.sqlite3"))
    store.save(ActiveSession("session", 0, 60, None, 40, "Pausado"))

    store.clear()

    assert store.load() is None
