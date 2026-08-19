from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from lembrete_agua.models import PlanMode, PlanStrategy, Preferences
from lembrete_agua.validation import ValidationError, validate_automatic, validate_manual


def user_config_dir() -> Path:
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "lembrete-agua"


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or user_config_dir() / "config.json"

    def load(self) -> Preferences:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return Preferences()
            autostart = data.get("autostart", False)
            if not isinstance(autostart, bool):
                return Preferences()
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
        except (OSError, json.JSONDecodeError, ValidationError, ValueError):
            return Preferences()

    def save(self, preferences: Preferences) -> None:
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        payload = {
            "sips": preferences.sips,
            "interval": preferences.interval,
            "unit": preferences.unit.value,
            "target_ml": preferences.target_ml,
            "duration": preferences.duration,
            "duration_unit": preferences.duration_unit.value,
            "plan_mode": preferences.plan_mode.value,
            "strategy": preferences.strategy.value,
            "autostart": preferences.autostart,
        }
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=".config-",
                suffix=".tmp",
                delete=False,
            ) as temporary:
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
