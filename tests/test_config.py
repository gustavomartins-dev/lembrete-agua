import json
from pathlib import Path

import pytest

import lembrete_agua.config as config_module
from lembrete_agua.config import ConfigStore
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
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["sips"] == 4
    assert data["strategy"] == "leve"
    assert list(path.parent.glob("*.tmp")) == []


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
    path = tmp_path / "config.json"
    path.write_text(content, encoding="utf-8")
    assert ConfigStore(path).load() == Preferences()


def test_previous_config_is_safely_migrated_to_defaults(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        '{"target_ml": 500, "duration": 2, "unit": "horas"}',
        encoding="utf-8",
    )
    assert ConfigStore(path).load() == Preferences()


def test_missing_config_uses_defaults(tmp_path: Path) -> None:
    assert ConfigStore(tmp_path / "missing.json").load() == Preferences()


def test_windows_config_uses_appdata(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(config_module.sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path))

    assert config_module.user_config_dir() == tmp_path / "Lembrete de Agua"
