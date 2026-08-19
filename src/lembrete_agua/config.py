from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from lembrete_agua.models import Preferences
from lembrete_agua.validation import ValidationError, parse_preferences


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
            return parse_preferences(
                data.get("target_ml"),
                data.get("duration"),
                data.get("unit"),
                autostart=autostart,
            )
        except (OSError, json.JSONDecodeError, ValidationError):
            return Preferences()

    def save(self, preferences: Preferences) -> None:
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        payload = {
            "target_ml": preferences.target_ml,
            "duration": preferences.duration,
            "unit": preferences.unit.value,
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
