import json
from pathlib import Path

import pytest

from lembrete_agua.config import ConfigStore
from lembrete_agua.models import DurationUnit, Preferences


def test_save_and_load_preferences(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "config.json"
    store = ConfigStore(path)
    expected = Preferences(750, 3, DurationUnit.HOURS, True)

    store.save(expected)

    assert store.load() == expected
    assert json.loads(path.read_text(encoding="utf-8"))["target_ml"] == 750
    assert list(path.parent.glob("*.tmp")) == []


@pytest.mark.parametrize(
    "content",
    [
        "not-json",
        "[]",
        '{"target_ml": 0, "duration": 2, "unit": "horas"}',
        '{"target_ml": 500, "duration": 2, "unit": "semanas"}',
        '{"target_ml": 500, "duration": "x", "unit": "horas"}',
        '{"target_ml": 500, "duration": 2, "unit": "horas", "autostart": "sim"}',
    ],
)
def test_invalid_config_uses_defaults(tmp_path: Path, content: str) -> None:
    path = tmp_path / "config.json"
    path.write_text(content, encoding="utf-8")
    assert ConfigStore(path).load() == Preferences()


def test_old_config_is_safely_migrated_to_defaults(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        '{"interval": 30, "unit": "minutos", "sips": 5}',
        encoding="utf-8",
    )
    assert ConfigStore(path).load() == Preferences()


def test_missing_config_uses_defaults(tmp_path: Path) -> None:
    assert ConfigStore(tmp_path / "missing.json").load() == Preferences()
