from __future__ import annotations

from collections.abc import Callable
from typing import Any

NOTIFICATION_TITLE = "Hora de beber água 💧"


def reminder_message(sips: int) -> str:
    noun = "gole" if sips == 1 else "goles"
    return f"Beba {sips} {noun} de água"


class WindowsNotificationService:
    """Envia toasts nativos no Windows mantendo o callback testável."""

    def __init__(
        self,
        on_activated: Callable[[str], None],
        on_accepted: Callable[[str], None] | None = None,
        *,
        toaster: Any | None = None,
        toast_factory: Callable[[], Any] | None = None,
        button_factory: Callable[[str, str], Any] | None = None,
        toast_duration: Any | None = None,
        toast_scenario: Any | None = None,
    ) -> None:
        if toaster is None or toast_factory is None:
            from windows_toasts import (
                Toast,
                ToastButton,
                ToastDuration,
                ToastScenario,
                WindowsToaster,
            )

            toaster = toaster or WindowsToaster("Lembrete de Água")
            toast_factory = toast_factory or Toast
            button_factory = button_factory or ToastButton
            toast_duration = toast_duration or ToastDuration.Long
            toast_scenario = toast_scenario or ToastScenario.Reminder
        self._on_activated = on_activated
        self._on_accepted = on_accepted or on_activated
        self._toaster = toaster
        self._toast_factory = toast_factory
        self._button_factory = button_factory
        self._toast_duration = toast_duration
        self._toast_scenario = toast_scenario
        self._active_toasts: list[Any] = []

    def send(self, record_id: str, sips: int, milliliters: int) -> None:
        toast = self._toast_factory()
        toast.text_fields = [
            NOTIFICATION_TITLE,
            f"{reminder_message(sips)} ({milliliters} mL). Clique para confirmar.",
        ]
        if self._toast_duration is not None:
            toast.duration = self._toast_duration
        if self._toast_scenario is not None:
            toast.scenario = self._toast_scenario
        accept_action = f"accept:{record_id}"
        if self._button_factory is not None:
            toast.AddAction(self._button_factory("Confirmar agora", accept_action))
        toast.on_activated = lambda arguments: (
            self._on_accepted(record_id)
            if getattr(arguments, "arguments", None) == accept_action
            else self._on_activated(record_id)
        )
        self._active_toasts.append(toast)
        self._toaster.show_toast(toast)

    def clear(self) -> None:
        """Remove do Windows todos os toasts publicados pelo aplicativo."""
        self._toaster.clear_toasts()
        self._active_toasts.clear()
