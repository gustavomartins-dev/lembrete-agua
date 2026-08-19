from __future__ import annotations

import subprocess
from collections.abc import Callable, Sequence

NOTIFICATION_TITLE = "Hora de beber água 💧"


def reminder_message(sips: int) -> str:
    noun = "gole" if sips == 1 else "goles"
    return f"Beba {sips} {noun} de água"


class NotificationService:
    def __init__(
        self,
        runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    ) -> None:
        self._runner = runner

    def send(self, sips: int) -> bool:
        command: Sequence[str] = (
            "notify-send",
            "--app-name=Lembrete de Água",
            "--icon=dialog-information",
            NOTIFICATION_TITLE,
            reminder_message(sips),
        )
        try:
            result = self._runner(command, check=False, timeout=10, text=True)
        except (OSError, subprocess.TimeoutExpired):
            return False
        return result.returncode == 0
