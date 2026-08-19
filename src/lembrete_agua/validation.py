from __future__ import annotations

from lembrete_agua.models import IntervalUnit, Preferences


class ValidationError(ValueError):
    """Erro de entrada que pode ser exibido diretamente na interface."""


def positive_integer(value: object, field_name: str) -> int:
    if isinstance(value, bool):
        raise ValidationError(f"{field_name} deve ser um número inteiro maior que zero.")
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError) as error:
        raise ValidationError(
            f"{field_name} deve ser um número inteiro maior que zero."
        ) from error
    if number <= 0:
        raise ValidationError(f"{field_name} deve ser maior que zero.")
    return number


def parse_preferences(
    interval: object,
    unit: object,
    sips: object,
    *,
    autostart: bool = False,
) -> Preferences:
    try:
        parsed_unit = IntervalUnit(str(unit))
    except ValueError as error:
        raise ValidationError("Selecione minutos ou horas para o intervalo.") from error

    return Preferences(
        interval=positive_integer(interval, "O intervalo"),
        unit=parsed_unit,
        sips=positive_integer(sips, "A quantidade de goles"),
        autostart=bool(autostart),
    )
