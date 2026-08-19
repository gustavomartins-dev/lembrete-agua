import json
from pathlib import Path

import pytest

import lembrete_agua.config_path as config_path_module
from lembrete_agua.config import ConfigStore
from lembrete_agua.database import Database
from lembrete_agua.models import PlanMode, PlanStrategy, Preferences, TimeUnit


def test_save_and_load_all_plan_preferences(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "config.json"
    store = ConfigStore(path)
    expected = Preferences(
        sips=4,
        interval=20,
        unit=TimeUnit.MINUTES,
        target_ml=750,
        duration=3,
        duration_unit=TimeUnit.HOURS,
        plan_mode=PlanMode.AUTOMATIC,
        strategy=PlanStrategy.LIGHT,
        autostart=True,
    )

    store.save(expected)

    assert store.load() == expected
    data = Database(path).get_json("settings", "preferences")
    assert data is not None
    assert data["sips"] == 4
    assert data["strategy"] == "leve"


@pytest.mark.parametrize(
    "content",
    [
        "not-json",
        "[]",
        '{"sips": 0}',
        '{"sips": 5, "interval": 20, "unit": "dias"}',
        '{"sips": 5, "interval": 20, "unit": "minutos", "target_ml": 500}',
        (
            '{"sips": 5, "interval": 20, "unit": "minutos", "target_ml": 500, '
            '"duration": 2, "duration_unit": "horas", "autostart": "sim"}'
        ),
    ],
)
def test_invalid_config_uses_defaults(tmp_path: Path, content: str) -> None:
    path = tmp_path / "settings.sqlite3"
    try:
        value = json.loads(content)
    except ValueError:
        path.write_text(content, encoding="utf-8")
    else:
        if isinstance(value, dict):
            Database(path).set_json("settings", value, "preferences")
        else:
            Database(path).set_json("settings", {"invalid": value}, "preferences")
    assert ConfigStore(path).load() == Preferences()


def test_previous_config_is_safely_migrated_to_defaults(tmp_path: Path) -> None:
    path = tmp_path / "settings.sqlite3"
    Database(path).set_json(
        "settings",
        {"target_ml": 500, "duration": 2, "unit": "horas"},
        "preferences",
    )
    assert ConfigStore(path).load() == Preferences()


def test_missing_config_uses_defaults(tmp_path: Path) -> None:
    assert ConfigStore(tmp_path / "missing.json").load() == Preferences()


def test_windows_config_uses_appdata(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(config_path_module.sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path))

    assert config_path_module.user_config_dir() == tmp_path / "Lembrete de Agua"
