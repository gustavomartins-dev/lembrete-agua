import json
from pathlib import Path

import pytest

from lembrete_agua.config import ConfigStore
from lembrete_agua.models import IntervalUnit, Preferences


def test_save_and_load_preferences(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "config.json"
    store = ConfigStore(path)
    expected = Preferences(3, IntervalUnit.HOURS, 8, True)

    store.save(expected)

    assert store.load() == expected
    assert json.loads(path.read_text(encoding="utf-8"))["sips"] == 8
    assert list(path.parent.glob("*.tmp")) == []


@pytest.mark.parametrize(
    "content",
    [
        "not-json",
        "[]",
        '{"interval": 0, "unit": "minutos", "sips": 5}',
        '{"interval": 5, "unit": "semanas", "sips": 5}',
        '{"interval": 5, "unit": "minutos", "sips": "x"}',
        '{"interval": 5, "unit": "minutos", "sips": 2, "autostart": "sim"}',
    ],
)
def test_invalid_config_uses_defaults(tmp_path: Path, content: str) -> None:
    path = tmp_path / "config.json"
    path.write_text(content, encoding="utf-8")

    assert ConfigStore(path).load() == Preferences()


def test_missing_config_uses_defaults(tmp_path: Path) -> None:
    assert ConfigStore(tmp_path / "missing.json").load() == Preferences()

