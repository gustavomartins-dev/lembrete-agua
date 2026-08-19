from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lembrete_agua.config_path import user_config_dir


def default_database_path() -> Path:
    return user_config_dir() / "lembrete-agua.sqlite3"


class Database:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_database_path()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        self.path.chmod(0o600)
        connection.row_factory = sqlite3.Row
        try:
            self._create_schema(connection)
            yield connection
            connection.commit()
        finally:
            connection.close()

    @staticmethod
    def _create_schema(connection: sqlite3.Connection) -> None:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reminders (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                scheduled_at TEXT NOT NULL,
                sips INTEGER NOT NULL,
                milliliters INTEGER NOT NULL,
                status TEXT NOT NULL,
                responded_at TEXT
            );
            CREATE TABLE IF NOT EXISTS active_session (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                payload TEXT NOT NULL
            );
            """
        )

    def get_json(self, table: str, key: str | int = 1) -> dict[str, Any] | None:
        if table == "settings":
            query, parameters = "SELECT value FROM settings WHERE key = ?", (str(key),)
        elif table == "active_session":
            query, parameters = "SELECT payload FROM active_session WHERE id = ?", (int(key),)
        else:
            raise ValueError("Tabela de documento inválida.")
        with self.connect() as connection:
            row = connection.execute(query, parameters).fetchone()
        if row is None:
            return None
        value = row[0]
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else None

    def set_json(self, table: str, value: dict[str, Any], key: str | int = 1) -> None:
        payload = json.dumps(value, ensure_ascii=False)
        with self.connect() as connection:
            if table == "settings":
                connection.execute(
                    "INSERT OR REPLACE INTO settings(key, value) VALUES (?, ?)",
                    (str(key), payload),
                )
            elif table == "active_session":
                connection.execute(
                    "INSERT OR REPLACE INTO active_session(id, payload) VALUES (?, ?)",
                    (int(key), payload),
                )
            else:
                raise ValueError("Tabela de documento inválida.")

    def delete_active_session(self) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM active_session WHERE id = 1")


@dataclass(frozen=True, slots=True)
class ActiveSession:
    session_id: str
    reminder_number: int
    interval_seconds: float
    deadline: float | None
    paused_remaining: float | None
    state: str


class ActiveSessionStore:
    def __init__(self, database: Database | None = None) -> None:
        self.database = database or Database()

    def load(self) -> ActiveSession | None:
        try:
            data = self.database.get_json("active_session")
            return ActiveSession(**data) if data is not None else None
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return None

    def save(self, session: ActiveSession) -> None:
        self.database.set_json(
            "active_session",
            {
                "session_id": session.session_id,
                "reminder_number": session.reminder_number,
                "interval_seconds": session.interval_seconds,
                "deadline": session.deadline,
                "paused_remaining": session.paused_remaining,
                "state": session.state,
            },
        )

    def clear(self) -> None:
        self.database.delete_active_session()
