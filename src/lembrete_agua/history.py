from __future__ import annotations

import json
import os
import tempfile
import uuid
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from lembrete_agua.config import user_config_dir


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
        self.path = path or user_config_dir() / "history.json"

    def load(self) -> list[ReminderRecord]:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(raw, list):
            return []
        records: list[ReminderRecord] = []
        for item in raw:
            try:
                if not isinstance(item, dict):
                    continue
                records.append(
                    ReminderRecord(
                        id=str(item["id"]),
                        session_id=str(item["session_id"]),
                        scheduled_at=str(item["scheduled_at"]),
                        sips=int(item["sips"]),
                        milliliters=int(item["milliliters"]),
                        status=ReminderStatus(str(item["status"])),
                        responded_at=(
                            str(item["responded_at"]) if item.get("responded_at") else None
                        ),
                    )
                )
            except (KeyError, TypeError, ValueError):
                continue
        return records

    def add(self, record: ReminderRecord) -> None:
        records = self.load()
        records.append(record)
        self._save(records)

    def get(self, record_id: str) -> ReminderRecord | None:
        return next((record for record in self.load() if record.id == record_id), None)

    def respond(self, record_id: str, drank: bool) -> ReminderRecord | None:
        records = self.load()
        updated: ReminderRecord | None = None
        for index, record in enumerate(records):
            if record.id != record_id:
                continue
            updated = replace(
                record,
                status=ReminderStatus.DRANK if drank else ReminderStatus.SKIPPED,
                responded_at=datetime.now(UTC).isoformat(),
            )
            records[index] = updated
            break
        if updated is not None:
            self._save(records)
        return updated

    def _save(self, records: list[ReminderRecord]) -> None:
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=".history-",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                payload = [
                    {**asdict(record), "status": record.status.value} for record in records
                ]
                json.dump(payload, temporary, ensure_ascii=False, indent=2)
                temporary.write("\n")
                temporary.flush()
                os.fsync(temporary.fileno())
                temporary_path = Path(temporary.name)
            temporary_path.chmod(0o600)
            os.replace(temporary_path, self.path)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()

