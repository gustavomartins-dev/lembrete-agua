import pytest

from lembrete_agua.models import TimeUnit
from lembrete_agua.validation import (
    ValidationError,
    positive_integer,
    validate_automatic,
    validate_manual,
)


@pytest.mark.parametrize("value", [0, -1, "", "abc", "1.5", None, True])
def test_positive_integer_rejects_invalid_values(value: object) -> None:
    with pytest.raises(ValidationError):
        positive_integer(value, "O valor")


def test_validate_manual_configuration() -> None:
    assert validate_manual("4", "20", "minutos") == (4, 20, TimeUnit.MINUTES)


def test_validate_automatic_configuration() -> None:
    assert validate_automatic("750", "2", "horas") == (750, 2, TimeUnit.HOURS)


def test_validation_rejects_unknown_unit() -> None:
    with pytest.raises(ValidationError, match="minutos ou horas"):
        validate_manual("5", "20", "dias")


def test_automatic_validation_limits_unreasonable_volume() -> None:
    with pytest.raises(ValidationError, match="10.000"):
        validate_automatic("10001", "2", "horas")
