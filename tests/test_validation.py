import pytest

from lembrete_agua.models import IntervalUnit
from lembrete_agua.validation import ValidationError, parse_preferences, positive_integer


@pytest.mark.parametrize("value", [0, -1, "", "abc", "1.5", None, True])
def test_positive_integer_rejects_invalid_values(value: object) -> None:
    with pytest.raises(ValidationError):
        positive_integer(value, "O valor")


def test_parse_preferences_converts_valid_values() -> None:
    preferences = parse_preferences("2", "horas", "5", autostart=True)

    assert preferences.interval == 2
    assert preferences.unit is IntervalUnit.HOURS
    assert preferences.sips == 5
    assert preferences.autostart is True
    assert preferences.interval_seconds == 7_200


def test_parse_preferences_rejects_unknown_unit() -> None:
    with pytest.raises(ValidationError, match="minutos ou horas"):
        parse_preferences("2", "dias", "5")

