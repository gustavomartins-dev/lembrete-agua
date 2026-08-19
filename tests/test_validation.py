import pytest

from lembrete_agua.models import DurationUnit
from lembrete_agua.validation import ValidationError, parse_preferences, positive_integer


@pytest.mark.parametrize("value", [0, -1, "", "abc", "1.5", None, True])
def test_positive_integer_rejects_invalid_values(value: object) -> None:
    with pytest.raises(ValidationError):
        positive_integer(value, "O valor")


def test_parse_preferences_converts_valid_values() -> None:
    preferences = parse_preferences("750", "2", "horas", autostart=True)

    assert preferences.target_ml == 750
    assert preferences.duration == 2
    assert preferences.unit is DurationUnit.HOURS
    assert preferences.autostart is True
    assert preferences.duration_seconds == 7_200


def test_parse_preferences_rejects_unknown_unit() -> None:
    with pytest.raises(ValidationError, match="minutos ou horas"):
        parse_preferences("500", "2", "dias")


def test_parse_preferences_limits_unreasonable_volume() -> None:
    with pytest.raises(ValidationError, match="10.000"):
        parse_preferences("10001", "2", "horas")
