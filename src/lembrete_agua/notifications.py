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
        *,
        toaster: Any | None = None,
        toast_factory: Callable[[], Any] | None = None,
    ) -> None:
        if toaster is None or toast_factory is None:
            from windows_toasts import Toast, WindowsToaster

            toaster = toaster or WindowsToaster("Lembrete de Água")
            toast_factory = toast_factory or Toast
        self._on_activated = on_activated
        self._toaster = toaster
        self._toast_factory = toast_factory
        self._active_toasts: list[Any] = []

    def send(self, record_id: str, sips: int, milliliters: int) -> None:
        toast = self._toast_factory()
        toast.text_fields = [
            NOTIFICATION_TITLE,
            f"{reminder_message(sips)} ({milliliters} mL). Clique para confirmar.",
        ]
        toast.on_activated = lambda _arguments: self._on_activated(record_id)
        self._active_toasts.append(toast)
        self._toaster.show_toast(toast)
