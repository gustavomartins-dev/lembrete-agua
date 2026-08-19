from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from lembrete_agua.config_path import user_config_dir
from lembrete_agua.database import Database
from lembrete_agua.models import PlanMode, PlanStrategy, Preferences
from lembrete_agua.validation import ValidationError, validate_automatic, validate_manual


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        self.database = Database(path)
        self.path = self.database.path
        self.legacy_path = user_config_dir() / "config.json" if path is None else None

    def load(self) -> Preferences:
        try:
            data = self.database.get_json("settings", "preferences")
            if data is None and self.legacy_path is not None and self.legacy_path.exists():
                legacy = json.loads(self.legacy_path.read_text(encoding="utf-8"))
                data = legacy if isinstance(legacy, dict) else None
            preferences = self._parse(data)
            if data is not None and self.database.get_json("settings", "preferences") is None:
                self.save(preferences)
            return preferences
        except (
            OSError,
            sqlite3.DatabaseError,
            json.JSONDecodeError,
            ValidationError,
            ValueError,
            TypeError,
        ):
            return Preferences()

    @staticmethod
    def _parse(data: dict[str, Any] | None) -> Preferences:
        if data is None:
            return Preferences()
        autostart = data.get("autostart", True)
        if not isinstance(autostart, bool):
            raise ValidationError("Configuração de início automático inválida.")
        sips, interval, unit = validate_manual(
            data.get("sips"), data.get("interval"), data.get("unit")
        )
        target_ml, duration, duration_unit = validate_automatic(
            data.get("target_ml"), data.get("duration"), data.get("duration_unit")
        )
        return Preferences(
            sips=sips,
            interval=interval,
            unit=unit,
            target_ml=target_ml,
            duration=duration,
            duration_unit=duration_unit,
            plan_mode=PlanMode(str(data.get("plan_mode", PlanMode.MANUAL))),
            strategy=PlanStrategy(str(data.get("strategy", PlanStrategy.BALANCED))),
            autostart=autostart,
        )

    def save(self, preferences: Preferences) -> None:
        self.database.set_json(
            "settings",
            {
                "sips": preferences.sips,
                "interval": preferences.interval,
                "unit": preferences.unit.value,
                "target_ml": preferences.target_ml,
                "duration": preferences.duration,
                "duration_unit": preferences.duration_unit.value,
                "plan_mode": preferences.plan_mode.value,
                "strategy": preferences.strategy.value,
                "autostart": preferences.autostart,
            },
            "preferences",
        )
