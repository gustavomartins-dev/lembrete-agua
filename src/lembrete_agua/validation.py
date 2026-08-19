from __future__ import annotations

from lembrete_agua.models import DurationUnit, Preferences


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
    target_ml: object,
    duration: object,
    unit: object,
    *,
    autostart: bool = False,
) -> Preferences:
    try:
        parsed_unit = DurationUnit(str(unit))
    except ValueError as error:
        raise ValidationError("Selecione minutos ou horas para o prazo.") from error

    parsed_ml = positive_integer(target_ml, "A quantidade em mL")
    parsed_duration = positive_integer(duration, "O prazo")
    if parsed_ml > 10_000:
        raise ValidationError("A quantidade deve ser de no máximo 10.000 mL.")
    return Preferences(parsed_ml, parsed_duration, parsed_unit, bool(autostart))
