from __future__ import annotations

from lembrete_agua.models import TimeUnit


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


def parse_time_unit(value: object, field_name: str = "a unidade") -> TimeUnit:
    try:
        return TimeUnit(str(value))
    except ValueError as error:
        raise ValidationError(f"Selecione minutos ou horas para {field_name}.") from error


def validate_manual(sips: object, interval: object, unit: object) -> tuple[int, int, TimeUnit]:
    return (
        positive_integer(sips, "A quantidade de goles"),
        positive_integer(interval, "O intervalo"),
        parse_time_unit(unit, "o intervalo"),
    )


def validate_automatic(
    target_ml: object,
    duration: object,
    unit: object,
) -> tuple[int, int, TimeUnit]:
    parsed_ml = positive_integer(target_ml, "A quantidade em mL")
    if parsed_ml > 10_000:
        raise ValidationError("A quantidade deve ser de no máximo 10.000 mL.")
    return (
        parsed_ml,
        positive_integer(duration, "O prazo"),
        parse_time_unit(unit, "o prazo"),
    )
