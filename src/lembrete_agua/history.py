from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from lembrete_agua.config_path import user_config_dir
from lembrete_agua.database import Database


class ReminderStatus(StrEnum):
    PENDING = "pendente"
    DRANK = "bebeu"
    SKIPPED = "não bebeu"


@dataclass(frozen=True, slots=True)
class ReminderRecord:
    id: str
    session_id: str
    scheduled_at: str
    sips: int
    milliliters: int
    status: ReminderStatus = ReminderStatus.PENDING
    responded_at: str | None = None

    @classmethod
    def create(cls, session_id: str, sips: int, milliliters: int) -> ReminderRecord:
        return cls(
            id=str(uuid.uuid4()),
            session_id=session_id,
            scheduled_at=datetime.now(UTC).isoformat(),
            sips=sips,
            milliliters=milliliters,
        )


class HistoryStore:
    def __init__(self, path: Path | None = None) -> None:
        self.database = Database(path)
        self.path = self.database.path
        self.legacy_path = user_config_dir() / "history.json" if path is None else None

    def load(self) -> list[ReminderRecord]:
        try:
            with self.database.connect() as connection:
                rows = connection.execute(
                    "SELECT * FROM reminders ORDER BY scheduled_at"
                ).fetchall()
        except sqlite3.DatabaseError:
            return []
        if not rows and self.legacy_path is not None and self.legacy_path.exists():
            try:
                raw = json.loads(self.legacy_path.read_text(encoding="utf-8"))
                for item in raw if isinstance(raw, list) else []:
                    record = self._parse_legacy(item)
                    if record is not None:
                        self.add(record)
                return self.load()
            except (OSError, json.JSONDecodeError):
                return []
        return [self._from_row(row) for row in rows]

    @staticmethod
    def _from_row(row: object) -> ReminderRecord:
        return ReminderRecord(
            id=str(row["id"]),
            session_id=str(row["session_id"]),
            scheduled_at=str(row["scheduled_at"]),
            sips=int(row["sips"]),
            milliliters=int(row["milliliters"]),
            status=ReminderStatus(str(row["status"])),
            responded_at=str(row["responded_at"]) if row["responded_at"] else None,
        )

    @staticmethod
    def _parse_legacy(item: object) -> ReminderRecord | None:
        try:
            if not isinstance(item, dict):
                return None
            return ReminderRecord(
                id=str(item["id"]),
                session_id=str(item["session_id"]),
                scheduled_at=str(item["scheduled_at"]),
                sips=int(item["sips"]),
                milliliters=int(item["milliliters"]),
                status=ReminderStatus(str(item["status"])),
                responded_at=str(item["responded_at"]) if item.get("responded_at") else None,
            )
        except (KeyError, TypeError, ValueError):
            return None

    def add(self, record: ReminderRecord) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO reminders
                    (id, session_id, scheduled_at, sips, milliliters, status, responded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.session_id,
                    record.scheduled_at,
                    record.sips,
                    record.milliliters,
                    record.status.value,
                    record.responded_at,
                ),
            )

    def get(self, record_id: str) -> ReminderRecord | None:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM reminders WHERE id = ?", (record_id,)
            ).fetchone()
        return self._from_row(row) if row is not None else None

    def respond(self, record_id: str, drank: bool) -> ReminderRecord | None:
        with self.database.connect() as connection:
            cursor = connection.execute(
                "UPDATE reminders SET status = ?, responded_at = ? WHERE id = ?",
                (
                    (ReminderStatus.DRANK if drank else ReminderStatus.SKIPPED).value,
                    datetime.now(UTC).isoformat(),
                    record_id,
                ),
            )
        return self.get(record_id) if cursor.rowcount else None
