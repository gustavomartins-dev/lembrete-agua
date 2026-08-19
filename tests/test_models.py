import pytest

from lembrete_agua.models import DurationUnit, Preferences, build_hydration_plan


def test_plan_distributes_volume_into_regular_reminders() -> None:
    plan = build_hydration_plan(Preferences(500, 2, DurationUnit.HOURS))

    assert plan.total_sips == 20
    assert plan.reminder_count == 4
    assert plan.interval_seconds == 1_800
    assert [plan.sips_for_reminder(index) for index in range(1, 5)] == [5, 5, 5, 5]
    assert [plan.milliliters_for_reminder(index) for index in range(1, 5)] == [125] * 4


def test_plan_adjusts_last_reminder_to_exact_volume() -> None:
    plan = build_hydration_plan(Preferences(260, 60, DurationUnit.MINUTES))

    assert plan.total_sips == 11
    assert plan.reminder_count == 3
    assert [plan.sips_for_reminder(index) for index in range(1, 4)] == [5, 5, 1]
    assert [plan.milliliters_for_reminder(index) for index in range(1, 4)] == [125, 125, 10]


def test_plan_rejects_out_of_range_reminder() -> None:
    plan = build_hydration_plan(Preferences())
    with pytest.raises(ValueError):
        plan.sips_for_reminder(0)
