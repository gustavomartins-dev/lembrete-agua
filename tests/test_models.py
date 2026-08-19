import pytest

from lembrete_agua.models import (
    PlanStrategy,
    Preferences,
    TimeUnit,
    build_hydration_plan,
    build_manual_plan,
)


def test_manual_plan_repeats_selected_sips_and_interval() -> None:
    plan = build_manual_plan(Preferences(sips=4, interval=20, unit=TimeUnit.MINUTES))

    assert plan.is_repeating
    assert plan.interval_seconds == 1_200
    assert plan.sips_for_reminder(1) == 4
    assert plan.sips_for_reminder(100) == 4
    assert plan.milliliters_for_reminder(1) == 100


def test_balanced_plan_is_the_default_automatic_recommendation() -> None:
    plan = build_hydration_plan(Preferences(target_ml=500, duration=2))

    assert plan.strategy is PlanStrategy.BALANCED
    assert plan.total_sips == 20
    assert plan.reminder_count == 4
    assert plan.interval_seconds == 1_800
    assert [plan.sips_for_reminder(index) for index in range(1, 5)] == [5, 5, 5, 5]


def test_three_strategies_change_frequency_and_sips() -> None:
    preferences = Preferences(target_ml=500, duration=2)
    light = build_hydration_plan(preferences, PlanStrategy.LIGHT)
    balanced = build_hydration_plan(preferences, PlanStrategy.BALANCED)
    intensive = build_hydration_plan(preferences, PlanStrategy.INTENSIVE)

    assert light.reminder_count == 7
    assert balanced.reminder_count == 4
    assert intensive.reminder_count == 3
    assert light.fixed_sips == 3
    assert balanced.fixed_sips == 5
    assert intensive.fixed_sips == 8


def test_automatic_plan_adjusts_last_reminder_to_exact_volume() -> None:
    preferences = Preferences(target_ml=260, duration=60, duration_unit=TimeUnit.MINUTES)
    plan = build_hydration_plan(preferences)

    assert [plan.sips_for_reminder(index) for index in range(1, 4)] == [5, 5, 1]
    assert [plan.milliliters_for_reminder(index) for index in range(1, 4)] == [125, 125, 10]


def test_plan_rejects_out_of_range_reminder() -> None:
    plan = build_hydration_plan(Preferences())
    with pytest.raises(ValueError):
        plan.sips_for_reminder(0)
